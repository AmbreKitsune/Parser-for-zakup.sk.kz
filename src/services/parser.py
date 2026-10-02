from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
import time
import logging
import base64
import json
from urllib.parse import parse_qs, urlsplit

from cli.i18n import t

from services import save_data


def parser_site(*, logger: logging.Logger, url, driver: WebDriver,
                on_progress):
    items_id = []
    new_list_id = []
    old_list_id = set(save_data.get_data_old_id())
    wait = WebDriverWait(driver, 30, poll_frequency=0.25)

    search_path = "/eprocsearch/api/external/4dv3rts/filter"

    driver.execute_cdp_cmd("Network.enable", {
        "maxTotalBufferSize": 20_000_000,
        "maxResourceBufferSize": 5_000_000,
    })

    def wait_search(query_text, advert_status, page_number):
        requests = {}
        responses = {}
        finished = set()

        def read_response(browser):
            for entry in browser.get_log("performance"):
                event = json.loads(entry["message"])["message"]
                method = event["method"]
                params = event.get("params", {})
                request_id = params.get("requestId")

                if method == "Network.requestWillBeSent":
                    request = params["request"]
                    request_url = urlsplit(request["url"])

                    if (
                        request["method"] != "POST"
                        or request_url.path != search_path
                    ):
                        continue

                    body_text = request.get("postData")

                    if body_text is None:
                        body_text = browser.execute_cdp_cmd(
                            "Network.getRequestPostData",
                            {"requestId": request_id},
                        )["postData"]

                    body = json.loads(body_text)

                    if (
                        body.get("query", "") != query_text
                        or body.get("advertStatus") != advert_status
                        or body.get("lotStatus") != advert_status
                    ):
                        continue

                    requests[request_id] = request["url"]

                elif method == "Network.responseReceived":
                    responses[request_id] = params["response"]

                elif method == "Network.loadingFinished":
                    finished.add(request_id)

                elif method == "Network.loadingFailed":
                    if request_id in requests:
                        raise RuntimeError(
                            "Поисковый запрос не завершился: "
                            f"{params.get('errorText', 'неизвестная ошибка')}"
                        )

            for request_id, request_url in requests.items():
                response = responses.get(request_id)

                if response is None or request_id not in finished:
                    continue

                status = int(response["status"])

                if status != 200:
                    raise RuntimeError(
                        f"Поиск вернул HTTP {status}: {request_url}"
                    )

                result = browser.execute_cdp_cmd(
                    "Network.getResponseBody",
                    {"requestId": request_id},
                )

                body_text = result["body"]

                if result.get("base64Encoded"):
                    body_text = base64.b64decode(
                        body_text
                    ).decode("utf-8")

                data = json.loads(body_text)

                if not isinstance(data, list):
                    raise RuntimeError(
                        "Неожиданный формат ответа поиска: "
                        f"{request_url}"
                    )

                page_ids = []

                for item in data:
                    if not isinstance(item, dict):
                        raise RuntimeError(
                            "Некорректная запись в ответе поиска"
                        )

                    number = item.get("number")

                    if number is None or not str(number).strip():
                        raise RuntimeError(
                            "В ответе поиска отсутствует номер закупки"
                        )

                    page_ids.append(str(number).strip())

                logger.info(
                    "Ответ поиска: страница %s, HTTP %s, записей %s "
                    "| URL: %s",
                    page_number, status, len(page_ids), request_url,
                )

                # Обёртка нужна: пустой список тоже успешный результат.
                return {"ids": page_ids}

            return False

        return wait.until(
            read_response,
            message=(
                f"Не получен ответ поиска: {query_text!r}, "
                f"{advert_status}, страница {page_number}"
            ),
        )

    def read_rendered_page(browser, expected_ids):
        try:
            elements = [
                element
                for element in browser.find_elements(
                    By.CLASS_NAME,
                    "m-sidebar__layout--found-item",
                )
                if element.is_displayed()
            ]

            rendered_ids = [
                element.find_element(
                    By.CLASS_NAME,
                    "m-found-item__num",
                ).text.removeprefix("№").strip()
                for element in elements
            ]

            return rendered_ids == expected_ids

        except (StaleElementReferenceException, NoSuchElementException):
            return False

    def get_next_button(browser):
        try:
            next_li = browser.find_element(
                By.XPATH,
                '//li[contains(@class, "page-item") '
                'and .//a[@aria-label="Next"]]',
            )

            classes = (next_li.get_attribute("class") or "").split()

            if "disabled" in classes:
                return {"finished": True}

            button = next_li.find_element(By.TAG_NAME, "a")

            if not button.is_displayed() or not button.is_enabled():
                return False

            return {"finished": False, "button": button}

        except (StaleElementReferenceException, NoSuchElementException):
            return False

    url_start, url_q, url_end = url

    for query in url_q:
        for advert_status in url_end:
            current_url = (
                f"{url_start}{query}"
                f"&adst={advert_status}&lst={advert_status}"
            )

            query_text = parse_qs(
                urlsplit(current_url).fragment.partition("?")[2],
                keep_blank_values=True,
            ).get("q", [""])[0]

            # Новый документ исключает выдачу предыдущего запроса.
            driver.get("about:blank")
            driver.get_log("performance")
            driver.get(f"{current_url}&page=1")

            page_number = 1

            while True:
                result = wait_search(
                    query_text,
                    advert_status,
                    page_number,
                )
                page_ids = result["ids"]

                if not page_ids:
                    logger.info(
                        "Поиск вернул пустой список: %s | Страница %s",
                        current_url, page_number,
                    )
                    break

                # Проверяем, что HTML показывает именно полученный ответ.
                wait.until(
                    lambda browser: read_rendered_page(browser, page_ids),
                    message=(
                        f"Выдача не совпала с ответом поиска: "
                        f"{current_url}, страница {page_number}"
                    ),
                )

                logger.info(
                    "Страница %s: найдено закупок %s | URL: %s",
                    page_number, len(page_ids), current_url,
                )

                for item_id in page_ids:
                    if item_id not in items_id and item_id not in old_list_id:
                        items_id.append(item_id)

                    if item_id not in new_list_id:
                        new_list_id.append(item_id)

                on_progress(completed=len(new_list_id))

                next_result = wait.until(
                    get_next_button,
                    message="Не найдена кнопка следующей страницы",
                )

                if next_result["finished"]:
                    break

                # Отбрасываем события до следующего перехода.
                driver.get_log("performance")
                next_result["button"].click()
                page_number += 1

    logger.info(
        "Сбор номеров завершён: уникальных закупок %s, новых %s",
        len(new_list_id), len(items_id),
    )

    return items_id, new_list_id


def parser_local_site(*, logger: logging.Logger, site, items,
                      driver: WebDriver, on_progress):
    list_items = []
    wait = WebDriverWait(driver, 20, poll_frequency=0.5)

    modal_selector = 'ngb-modal-window:not([aria-hidden="true"])'

    def read_card(browser, expected_id):
        try:
            windows = browser.find_elements(
                By.CSS_SELECTOR,
                modal_selector,
            )
            visible_windows = [
                window for window in windows if window.is_displayed()
            ]

            if not visible_windows:
                return False

            modal = visible_windows[-1]

            item_id = modal.find_element(
                By.CSS_SELECTOR,
                ".m-modal__num",
            ).text.removeprefix("№").strip()

            if item_id != expected_id:
                return False

            name = modal.find_element(
                By.CSS_SELECTOR,
                ".m-modal__title",
            ).text.strip()

            info = modal.find_elements(
                By.CSS_SELECTOR,
                ".m-infoblock__layout.ng-star-inserted",
            )

            if not name or len(info) < 2:
                return False

            owner_text = info[0].text
            price_text = info[1].text

            if not owner_text.strip() or not price_text.strip():
                return False

            start_elements = modal.find_elements(
                By.CSS_SELECTOR,
                ".m-rangebox__layout:not(.m-rangebox__layout--rtl) "
                ".m-rangebox__date",
            )
            end_elements = modal.find_elements(
                By.CSS_SELECTOR,
                ".m-rangebox__layout--rtl .m-rangebox__date",
            )

            item = {
                "URL": f"{site}/#/ext(popup:item/{expected_id}/advert)",
                "ID": item_id,
                "START_DATE": (
                    start_elements[0].text if start_elements else ""
                ),
                "END_DATE": (
                    end_elements[0].text if end_elements else ""
                ),
                "NAME": name,
                "OWNER": owner_text[9:],
                "PRICE": price_text[18:],
            }

            return {"modal": modal, "item": item}

        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def close_card(modal):
        button = modal.find_element(
            By.CSS_SELECTOR,
            ".m-modal__close-button a",
        )

        if not button.is_displayed() or not button.is_enabled():
            return False

        try:
            button.click()
            return True
        except ElementClickInterceptedException:
            return False

    retry_errors = (
        TimeoutException,
        NoSuchElementException,
        StaleElementReferenceException,
        ElementClickInterceptedException,
    )

    for completed, expected_id in enumerate(items, start=1):
        expected_id = str(expected_id).strip()
        new_site = f"{site}/#/ext(popup:item/{expected_id}/advert)"

        for attempt in range(1, 4):
            try:
                driver.get(new_site)

                if attempt > 1:
                    driver.refresh()

                result = wait.until(
                    lambda browser: read_card(browser, expected_id),
                    message=f"Не загрузилась карточка №{expected_id}",
                )

                modal = result["modal"]

                wait.until(
                    lambda browser: close_card(modal),
                    message=f"Не удалось закрыть карточку №{expected_id}",
                )

                wait.until(
                    EC.staleness_of(modal),
                    message=f"Окно карточки №{expected_id} не удалилось",
                )

                for _ in range(5):
                    windows = driver.find_elements(
                        By.CSS_SELECTOR,
                        "ngb-modal-window",
                    )

                    if not windows:
                        break

                    def get_top_window(browser):
                        try:
                            visible_windows = [
                                window
                                for window in browser.find_elements(
                                    By.CSS_SELECTOR,
                                    modal_selector,
                                )
                                if window.is_displayed()
                            ]
                            return visible_windows[-1] if visible_windows else False
                        except StaleElementReferenceException:
                            return False

                    remaining_modal = wait.until(
                        get_top_window,
                        message="Оставшееся окно карточки не стало доступно",
                    )

                    wait.until(
                        lambda browser: close_card(remaining_modal),
                        message="Не удалось закрыть оставшееся окно карточки",
                    )

                    wait.until(
                        EC.staleness_of(remaining_modal),
                        message="Оставшееся окно карточки не удалилось",
                    )

                if driver.find_elements(By.CSS_SELECTOR, "ngb-modal-window"):
                    raise TimeoutException(
                        "После пяти закрытий остались окна карточек"
                    )

                list_items.append(result["item"])
                on_progress(completed=completed)
                break

            except retry_errors:
                if attempt == 3:
                    raise

                logger.warning(
                    "Карточка №%s: повторная попытка %s/3",
                    expected_id,
                    attempt + 1,
                    exc_info=True,
                )

    return list_items


def main_parser(*, logger, site, url, on_progress):
    on_progress(stage=t("starting_browser"))
    options = webdriver.EdgeOptions()
    options.set_capability("ms:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Edge(options=options)

    try:
        on_progress(stage=t("collecting_purchases"))
        items_list, new_list_id = parser_site(
            logger=logger,
            url=url,
            driver=driver,
            on_progress=on_progress,
        )

        on_progress(
            stage=t("collecting_cards"),
            completed=0,
            total=len(items_list),
        )
        items_data = parser_local_site(
            logger=logger,
            site=site,
            items=items_list,
            driver=driver,
            on_progress=on_progress,
        )
    finally:
        driver.quit()

    if items_data:
        return items_data, new_list_id
    return [], []

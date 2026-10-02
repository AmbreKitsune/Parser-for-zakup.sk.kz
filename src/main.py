import os

from core.config_builder import WorksConfigs
from core.exception_build import ErrorIncorrectData
from core.paths import DATA_DIR, LOG_FILE
from services import save_data
from services.parser import main_parser
from services.output import output
from cli.logger import setup_logger
from cli.status import ProcessStatus
from cli.i18n import init_language, t


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger = setup_logger()

    conf = WorksConfigs(logger=logger)
    
    try:
        init_language()
        conf.main_configs()
    except ErrorIncorrectData:
        logger.exception("Загрузка конфига прервана")
        return
    except KeyboardInterrupt:
        print(t("stopped"))
        logger.info("Остановлено пользователем")
        return
    
    site, url = conf.get_config()

    with ProcessStatus(logger) as status:
        try:
            output_path = None
            items, new_list_id = main_parser(
                logger=logger,
                site=site,
                url=url,
                on_progress=status.update,
            )

            if items:
                status.update(stage=t("saving_csv"))
                output_path = output(items_list=items)
                
                logger.info(
                    "CSV сохранён: %s | Записано закупок: %s",
                    output_path, len(items),
                )

            if new_list_id:
                save_data.save_data_old_id(new_list_id)

            status.update(
                stage=t("done") if items else t("no_new")
            )
            if output_path is not None:
                try:
                    os.startfile(output_path.parent)
                except OSError:
                    logger.exception("Не удалось открыть папку результатов")
        except KeyboardInterrupt:
            logger.warning("Работа остановлена пользователем")
            status.update(stage=t("stopped"))
        except Exception:
            logger.exception("Не удалось завершить обработку")
            status.update(
                stage=t("processing_failed", path=LOG_FILE)
            )


if __name__ == "__main__":
    main()

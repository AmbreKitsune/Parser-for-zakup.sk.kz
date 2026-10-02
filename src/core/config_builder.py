import os
import configparser
from cli import questions
from cli.questions import RussianIntPrompt
from cli.i18n import t
from core import exception_build
from core.paths import CONFIG_FILE, CONFIGS_DIR
from pathlib import Path
import logging

from rich.table import Table
from rich.console import Console
from rich.panel import Panel



class WorksConfigs:
    def __init__(self, *, logger: logging.Logger) -> None:
        self.logger = logger
        self.file_name: Path | None = None
        self.type_configs: str | None = None
        self.site: str | None = None
        self.url: str | None = None

        self.url_start: str | None = None
        self.url_q: list | None = None
        self.url_end: list | None = None

    def main_configs(self) -> None:
        while self.file_name is None:
            self.type_configs = self.check_file_config()
            
            if self.type_configs == "Folder":
                self.work_in_folder_configs()

            if self.type_configs == "Create":
                self.choosing_create_file_or_folder()

        self.reader_file_config()
        
        
    def check_file_config(self):
        if CONFIGS_DIR.is_dir():
            self.logger.info("Загрузка конфига с папки")
            return "Folder"
        if CONFIG_FILE.is_file():
            self.logger.info("Загрузка конфига с корневой папки")
            self.file_name = CONFIG_FILE
            return "File" 
        self.logger.info("Создание конфиг файла")
        return "Create"

    def choosing_create_file_or_folder(self):
        console = Console()

        console.print(
            Panel(
                t("create_options"),
                title=t("create_configuration"),
                border_style="cyan",
                expand=False,
            )
        )

        result = RussianIntPrompt.ask(
            t("select_option"),
            choices=["1", "2"],
            console=console,
        )

        if result == 1:
            self.file_name = CONFIG_FILE
            self.create_file_config()
        else:
            self.create_folders_configs()

    def create_file_config(self) -> None:
        config = configparser.ConfigParser(allow_no_value=True)
        
        # TODO: ДАННЫЕ ОТСЮДА, НЕ ИЗМЕНЯТЬ. БУДУ ЛОМАТЬ ПРОГРАММУ СРАЗУ!!!!
        config['GLOBAL'] = {
            "site": "https://zakup.sk.kz",
            "domain": "zakup.sk.kz"
        }

        config['EXT'] = {}
        
        tabs: str = questions.type_for_purchase()
        config['EXT']['tabs'] = tabs

        if tabs in ["lot", "advert"]:
            config['EXT']['q'] = questions.search_for_purchase()

            config['EXT']['s'] = questions.services()
            config['EXT']['w'] = questions.work()

            status_purchase = questions.status_for_purchase()
            config['EXT']['adst'] = ",".join(status_purchase)
            config['EXT']['lst'] = ",".join(status_purchase)
        else:
            # FIXME: заглушка, сразу уходим.
            raise exception_build.ErrorInWorking 

        with open(self.file_name, 'w', encoding="UTF-8") as file: # type: ignore
            config.write(file)
        
        self.logger.info("Файл конфига успешно был создан!")


    def create_folders_configs(self) -> None:
        CONFIGS_DIR.mkdir(exist_ok=True)

        config = configparser.ConfigParser(allow_no_value=True)
        
        # TODO: ДАННЫЕ ОТСЮДА, НЕ ИЗМЕНЯТЬ. БУДУ ЛОМАТЬ ПРОГРАММУ СРАЗУ!!!!
        config['GLOBAL'] = {
            "site": "https://zakup.sk.kz",
            "domain": "zakup.sk.kz"
        }

        config['EXT'] = {}
        
        tabs: str = questions.type_for_purchase()
        config['EXT']['tabs'] = tabs

        if tabs in ["lot", "advert"]:
            q = questions.search_for_purchase()
            list_q = q.split(',')
            config['EXT']['q'] = q

            config['EXT']['s'] = questions.services()
            config['EXT']['w'] = questions.work()

            status_purchase = questions.status_for_purchase()
            config['EXT']['adst'] = ",".join(status_purchase)
            config['EXT']['lst'] = ",".join(status_purchase)
        else:
            # FIXME: заглушка, сразу уходим.
            self.logger.error("Данная функция ещё не доступна!", exc_info=True)
            raise exception_build.ErrorInWorking 

        file_name = CONFIGS_DIR / "_".join(list_q)
        
        if file_name.exists():
            self.logger.error("Такая папка уже есть!", exc_info=True)
            return
        file_name.mkdir()
        
        with open(file_name / "config.ini", 'w', encoding="UTF-8") as file: # type: ignore
            config.write(file)
        
        self.logger.info("Папка с конфигом успешно была создана!")

    def work_in_folder_configs(self):
        items = sorted(
            (
                folder
                for folder in CONFIGS_DIR.iterdir()
                if folder.is_dir()
                and (folder / "config.ini").is_file()
            ),
            key=lambda folder: folder.name,
        )

        if not items:
            self.logger.info("В папке configs нет конфигов")
            self.choosing_create_file_or_folder()
            return

        console = Console()

        table = Table(title=t("available_configs"))
        table.add_column(t("number"), style="cyan", justify="right")
        table.add_column(t("config"))
        table.add_row("0", t("create_config"))

        for index, folder in enumerate(items, start=1):
            table.add_row(str(index), folder.name)

        console.print(table)

        index = RussianIntPrompt.ask(
            t("select_config"),
            choices=[str(number) for number in range(len(items) + 1)],
            console=console,
        )

        if index == 0:
            self.choosing_create_file_or_folder()
            return

        self.file_name = items[index - 1] / "config.ini"

    def reader_file_config(self):
        config = configparser.ConfigParser()
        files_read = config.read(self.file_name, encoding="UTF-8") # type: ignore
        
        if not files_read:
            self.logger.critical("Не правильная загрузка конфига с папки!", exc_info=True)
            raise exception_build.ErrorMissingConfigFile
        

        # FIXME: Начинаем идти по config.ini и выносить данные от туда
        if (
            not config.has_option("GLOBAL", "site")
            or not config.get("GLOBAL", "site").strip()
        ):
            os.remove(self.file_name)
            self.logger.critical("Конфиг повреждён и удалён")
            print(t("damaged_config"))
            raise exception_build.ErrorIncorrectData

        self.site = config["GLOBAL"]["site"]
    

        tabs = config['EXT']['tabs']
        q = config['EXT']['q'].split(",")
        s = config.getboolean('EXT', 's')
        w = config.getboolean('EXT', 'w')
        adst_lst = config['EXT']['adst']

        self.url_start = f"{self.site}/#/ext?"
        self.url_start += f"tabs={tabs}"
        if w:
            self.url_start += f"&w={w}"
        if s:
            self.url_start += f"&s={s}"
        
        self.url_q = []
        for i in q:
            self.url_q.append(f"&q={'%20'.join(i.split())}")
        
        self.url_end = adst_lst.split(",")
        # url_end = f"&adst={adst}&lst={lst}"

        self.logger.info("Конфиг успешно загружен")
    
    def get_config(self):
        return [self.site, [self.url_start, self.url_q, self.url_end]]




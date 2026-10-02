import json
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt

from core.paths import DATA_DIR

LOCALES_DIR = Path(__file__).resolve().parent / "locales"
SETTINGS_FILE = DATA_DIR / "settings.json"
LANGUAGES = ("ru", "en", "kk")


def load_locale(language):
    with open(LOCALES_DIR / f"{language}.json", encoding="utf-8") as file:
        return json.load(file)


_fallback = load_locale("ru")
_texts = _fallback


def t(key, **values):
    return _texts.get(key, _fallback.get(key, key)).format(**values)


class LanguagePrompt(Prompt):
    illegal_choice_message = (
        "[red]Введите ru, en или kk / "
        "Enter ru, en or kk / "
        "ru, en немесе kk енгізіңіз.[/red]"
    )


def init_language():
    global _texts

    settings = {}

    if SETTINGS_FILE.is_file():
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as file:
                loaded = json.load(file)
            if isinstance(loaded, dict):
                settings = loaded
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    language = settings.get("language")

    if language not in LANGUAGES:
        console = Console()
        console.print("Русский — ru | English — en | Қазақша — kk")

        language = LanguagePrompt.ask(
            "Язык / Language / Тіл",
            choices=list(LANGUAGES),
            console=console,
        )

        settings["language"] = language

        DATA_DIR.mkdir(exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(settings, file, ensure_ascii=False, indent=2)

    _texts = load_locale(language)

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

from cli.i18n import t

console = Console()


class RussianIntPrompt(IntPrompt):
    @classmethod
    def ask(cls, *args, **kwargs):
        cls.validate_error_message = f"[red]{t('invalid_integer')}[/red]"
        cls.illegal_choice_message = f"[red]{t('invalid_choice')}[/red]"
        return super().ask(*args, **kwargs)


def type_for_purchase() -> str:
    console.print(
        Panel(
            t("purchase_options"),
            title=t("purchase_type"),
            border_style="cyan",
            expand=False,
        )
    )

    choice = RussianIntPrompt.ask(
        t("answer"),
        choices=["1", "2"],
        console=console,
    )

    return {1: "lot", 2: "advert"}[choice]


def search_for_purchase() -> str:
    console.print(t("search_hint"))

    return Prompt.ask(t("answer"), default="", console=console)


def status_for_purchase() -> list[str]:
    console.print(
        Panel(
            t("status_options"),
            title=t("purchase_statuses"),
            border_style="cyan",
            expand=False,
        )
    )

    statuses = {
        "1": "PUBLISHED",
        "2": "DISCUSSION_PUBLISHED",
    }

    while True:
        answer = Prompt.ask(t("answer"), console=console)
        choices = [value.strip() for value in answer.split(",")]

        if all(choice in statuses for choice in choices):
            return list(
                dict.fromkeys(statuses[choice] for choice in choices)
            )

        console.print(f"[red]{t('invalid_status')}[/red]")


def services() -> str:
    console.print(
        Panel(
            t("yes_no"),
            title=t("exclude_services"),
            border_style="cyan",
            expand=False,
        )
    )

    choice = RussianIntPrompt.ask(
        t("answer"),
        choices=["1", "2"],
        default=2,
        console=console,
    )

    return "True" if choice == 1 else "False"


def work() -> str:
    console.print(
        Panel(
            t("yes_no"),
            title=t("exclude_works"),
            border_style="cyan",
            expand=False,
        )
    )

    choice = RussianIntPrompt.ask(
        t("answer"),
        choices=["1", "2"],
        default=2,
        console=console,
    )

    return "True" if choice == 1 else "False"

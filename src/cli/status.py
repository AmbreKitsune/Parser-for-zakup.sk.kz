import logging

from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from cli.i18n import t


class ProcessStatus(logging.Handler):
    def __init__(self, logger: logging.Logger):
        super().__init__(level=logging.WARNING)
        self.logger = logger
        self.stage = t("preparing")
        self.completed = 0
        self.total = None
        self.warnings = 0
        self.errors = 0
        self.live = Live(self.render(), auto_refresh=False)

    def render(self):
        text = Text()
        text.append(self.stage, style="bold cyan")

        if self.total is None:
            text.append("\n" + t("found", completed=self.completed))
        else:
            text.append(
                "\n" + t(
                    "processed",
                    completed=self.completed,
                    total=self.total,
                )
            )

        text.append(
            " | " + t("warnings", count=self.warnings),
            style="yellow",
        )
        text.append(
            " | " + t("errors", count=self.errors),
            style="red",
        )

        return Panel(text, title=t("parser_title"), border_style="cyan")

    def update(self, *, stage=None, completed=None, total=None):
        if stage is not None:
            self.stage = stage
        if completed is not None:
            self.completed = completed
        if total is not None:
            self.total = total

        self.live.update(self.render(), refresh=True)

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.errors += 1
        elif record.levelno >= logging.WARNING:
            self.warnings += 1

        self.live.update(self.render(), refresh=True)

    def __enter__(self):
        self.live.start(refresh=True)
        self.logger.addHandler(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.removeHandler(self)
        self.live.stop()
        self.close()

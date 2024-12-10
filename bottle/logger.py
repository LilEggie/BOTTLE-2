__all__ = ["StreamFormatter", "get_logger", "create_logger"]
__version__ = "1.0.0"
__author__ = "Eggie"


import logging
import logging.handlers

import bottle.ansi as ansi
import bottle.dir


class StreamFormatter(logging.Formatter):
    def __init__(self, *, stylize: bool = True) -> None:
        """
        Initializes a formatter for the stream.

        :param stylize: If the formatted string should be stylized using ANSI
            escape codes.
        """
        fmt = "{asctime}_{levelname}_{name}"
        datefmt = "%Y-%m-%d %H:%M:%S"
        super().__init__(fmt, datefmt, '{')

        self.stylize = stylize

    def format(self, record: logging.LogRecord) -> str:
        s = super().format(record).split("_")

        if not self.stylize:
            return f"[{s[0]}] [{s[1]:<8}] {s[2]}: {record.getMessage()}"

        style = ansi.bold + ansi.hex_color("5A6374")
        date = style + s[0] + ansi.reset

        style = ansi.bold
        match record.levelno:
            case logging.DEBUG | logging.INFO:
                style += ansi.hex_color("61AFEF")
            case logging.WARNING:
                style += ansi.hex_color("E5C07B")
            case logging.ERROR | logging.CRITICAL:
                style += ansi.hex_color("E06C75")
        levelname = style + f"{s[1]:<8}" + ansi.reset

        style = ansi.hex_color("C678DD")
        name = style + record.name + ansi.reset

        return f"{date} {levelname} {name} {record.getMessage()}"


__loggers: dict[str, logging.Logger]
__loggers = {}


def get_logger(name: str,
               *,
               level: int | str = logging.WARNING,
               stylize: bool = True) -> logging.Logger:
    """
    Gets the logger with the given name.

    If this logger doesn't exist, the logger will be created and cached.

    :param name: The name of the logger.
    :param level: The level number or name.
    :param stylize: If the formatted string should be stylized using ANSI
        escape codes.
    """
    if name not in __loggers:
        __loggers[name] = create_logger(name, level=level, stylize=stylize)
    return __loggers[name]


def create_logger(name: str,
                  *,
                  level: int | str = logging.WARNING,
                  stylize: bool = True) -> logging.Logger:
    """
    Creates and returns a logger with the given name.

    This logger will not be cached. See :meth:`get_logger`

    :param name: The name of the logger.
    :param level: The level number or name.
    :param stylize: If the formatted string should be stylized using ANSI
        escape codes.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(StreamFormatter(stylize=stylize))
    logger.addHandler(handler)

    return logger


#
#   BOTTLE
#
__bottle_logger = logging.getLogger("bottle")
__bottle_logger.setLevel(logging.WARNING)
__handler = logging.handlers.RotatingFileHandler(
    filename=bottle.dir.logs / "bottle.log",
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,
    backupCount=5
)
__handler.setFormatter(StreamFormatter(stylize=False))
__handler.setLevel(logging.WARNING)
__bottle_logger.addHandler(__handler)

get_logger("bottle.client", level=logging.DEBUG)
get_logger("bottle.player", level=logging.DEBUG)

#
#   DISCORD
#
__discord_logger = logging.getLogger("discord")
__discord_logger.setLevel(logging.DEBUG)

__handler = logging.handlers.RotatingFileHandler(
    filename=bottle.dir.logs / "discord.log",
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,
    backupCount=5
)
__handler.setFormatter(StreamFormatter(stylize=False))
__handler.setLevel(logging.DEBUG)
__discord_logger.addHandler(__handler)

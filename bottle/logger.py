__all__ = []
__version__ = "1.0.0"
__author__ = "Eggie"


import logging
from typing import Literal, Optional

import bottle.ansi as ansi


class StreamFormatter(logging.Formatter):
    """
    A customized formatter for stream output. This formatter supports ANSI
    escape codes.
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal["%", "{", "$"] = "%",
        *,
        ansi_supported: bool = True
    ) -> None:
        """
        Initializes the formatter with specified format strings.

        Initialize the formatter either with the specified format string, or a
        default as described above. Allow for specialized date formatting with
        the optional datefmt argument. If datefmt is omitted, you get an
        ISO8601-like (or RFC 3339-like) format.

        Use a style parameter of '%', '{' or '$' to specify that you want to
        use one of %-formatting, :meth:`str.format` (``{}``) formatting or
        :class:`string.Template` formatting in your format string.
        """
        if ansi_supported:
            if fmt:
                fmt = format(ansi.String(fmt))
            if datefmt:
                datefmt = format(ansi.String(datefmt))

        super().__init__(fmt, datefmt, style)

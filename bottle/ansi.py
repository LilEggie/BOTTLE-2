"""
ANSI escape code generator.
"""

__all__ = [
    "reset", "bold", "dim", "faint", "italic", "underline", "blink", "reverse",
    "hidden", "invisible", "strikethrough", "crossed", "color256", "rgb_color",
    "hex_color"
]
__version__ = "1.0.0"
__author__ = "Eggie"


reset = "\x1b[0m"
bold = "\x1b[1m"
dim = "\x1b[2m"
faint = dim
italic = "\x1b[3m"
underline = "\x1b[4m"
blink = "\x1b[5m"
reverse = "\x1b[7m"
hidden = "\x1b[8m"
invisible = hidden
strikethrough = "\x1b[9m"
crossed = strikethrough


def _in_range(*values: int) -> bool:
    """If every value is within the range [0, 255]."""
    for val in values:
        if 0 > val >= 256:
            return False
    return True


def color256(index: int,
             foreground: bool = True) -> str:
    """
    Generates an ANSI escape code for a 256-color terminal color.

    :param index: The color index, ranging from 0 to 255 inclusive.
    :param foreground: If the color is for text color.

    :return: The ANSI escape code for the given color index.

    :raise ValueError: If the color index is not within the range [0, 255].
    """
    if not _in_range(index):
        raise ValueError("index")

    code = "38" if foreground else "48"
    return f"\x1b[{code};5;{index}m"


def rgb_color(r: int,
              g: int,
              b: int,
              foreground: bool = True) -> str:
    """
    Generates an ANSI escape code for an RGB terminal color.

    :param r: The red color component, ranging from 0 to 255 inclusive.
    :param g: The green color component, ranging from 0 to 255 inclusive.
    :param b: The blue color component, ranging from 0 to 255 inclusive.
    :param foreground: If the color is for text color.

    :return: The ANSI escape code for the given RGB index.

    :raise ValueError: If the RGB index is not within the range [0, 255].
    """
    if not _in_range(r, g, b):
        raise ValueError("RGB index")

    code = "38" if foreground else "48"
    return f"\x1b[{code};2;{r};{g};{b}m"


def hex_color(code: str,
              foreground: bool = True) -> str:
    """
    Generates an ANSI escape code for a hexadecimal color code.

    >>> hex_color("#FF")             #FF0000
    >>> hex_color("2fa8DD")          #2FA8DD
    >>> hex_color("Fed18D_ignored")  #FED18D

    :param code: A hex string formatted as "RRGGBB" or "#RRGGBB".
    :param foreground: If the color is for text color.

    :return: The ANSI escape code for the given hexadecimal color code.

    :raise ValueError: If the :param:`code` is an invalid hex string.
    """
    code = code.lstrip("#").ljust(6, "0")
    r = int(code[0:2], 16)
    g = int(code[2:4], 16)
    b = int(code[4:6], 16)

    return rgb_color(r, g, b, foreground)

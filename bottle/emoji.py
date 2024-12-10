__all__ = ["get_tile_code"]
__version__ = "1.0.0"
__author__ = "Eggie"


import json
from typing import Optional

import bottle.dir
import bottle.simulators.wordle as wordle


__filepath = bottle.dir.resources / "emojis" / "tiles.json"
with open(__filepath, "r") as __file:
    __tile_emojis = json.load(__file)


def get_tile_code(tile: Optional[wordle.Tile]) -> str:
    """Returns the Discord emoji code for the tile."""
    emojis = __tile_emojis
    if tile is None:
        return emojis["blank_tile"]

    category = ""
    match tile.hint:
        case wordle.Hint.BLACK:
            category = "black_tiles"
        case wordle.Hint.GRAY:
            category = "gray_tiles"
        case wordle.Hint.YELLOW:
            category = "yellow_tiles"
        case wordle.Hint.GREEN:
            category = "green_tiles"

    return emojis[category][tile.char.lower()]

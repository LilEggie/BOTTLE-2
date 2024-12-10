"""
The Wordle game and its components.

The objective of the game involves figuring out a secret word. The player's
goal is to guess this secret word in as few attempts as possible by using the
color-coded hints the game provides.

==========   ===================================================
  Color      Description
==========   ===================================================
``BLACK``    The character has not been used in a guess yet.
``GRAY``     The character is not in the word at all.
``YELLOW``   The character is correct but in the wrong position.
``GREEN``    The character and its position are both correct.
==========   ===================================================
"""

__all__ = [
    "Hint", "Tile", "TileString", "WordleError", "NoAttemptsError",
    "WordleSimulator"
]
__version__ = "1.0.0"
__author__ = "Eggie"


from enum import IntEnum
from typing import Any, Optional


class Hint(IntEnum):
    """
    Enumeration representing the hint types for character tiles.

    Hint types are named after a color and are represented by integer values.
    These hints are ordered by accuracy, from unknown to 0% to 100%.

    Note that these colors serve to categorize a hint and do not necessarily
    imply visual representation.

    ==========   =====   ===================================================
      Color      Value   Description
    ==========   =====   ===================================================
    ``BLACK``      0     The character has not been used in a guess yet.
    ``GRAY``       1     The character is not in the word at all.
    ``YELLOW``     2     The character is correct but in the wrong position.
    ``GREEN``      3     The character and its position are both correct.
    ==========   =====   ===================================================
    """
    pass


class Tile:
    """
    A tile represents a character in a Wordle game, where each tile is assigned
    a hint on the character's accuracy.
    """

    def __init__(self,
                 char: str,
                 hint: Hint) -> None:
        """
        Initializes a tile object representing the given character.

        :param char: The character this tile represents.
        :param hint: The hint indicating the accuracy of the character this
            tile represents. Defaults to :class:`Hint.BLACK` indicating that
            the character has not been used yet.
        """
        raise NotImplementedError


class TileString(tuple[Tile]):
    """A tuple of tiles."""
    pass


class WordleError(Exception):
    """A Wordle error."""
    pass


class NoAttemptsError(WordleError):
    """No attempts remaining to make a guess."""
    pass


class WordleSimulator:
    """
    A Wordle simulator.
    """

    def __init__(self,
                 secret_word: str,
                 max_attempts: int) -> None:
        """
        Initializes a Wordle simulator.

        :param secret_word: The word the player is trying to guess.
        :param max_attempts: The maximum number of attempts the player has to
            guess the secret word. If this is a negative number, then the
            player will have an unlimited number of attempts. Defaults to -1.
        """
        raise NotImplementedError

    def has_attempts_left(self) -> bool:
        """If the player can make another attempt at a guess."""
        raise NotImplementedError

    def has_guessed_word(self) -> bool:
        """If the player has guessed the secret word."""
        raise NotImplementedError

    def terminate(self, flag: bool = True) -> None:
        """Quits the game."""
        raise NotImplementedError

    def is_terminated(self) -> bool:
        """If the game has been terminated."""
        raise NotImplementedError

    def reset(self,
              secret_word: Optional[str] = None,
              max_attempts: Optional[int] = None,
              *args: Any,
              **kwargs: Any) -> None:
        """
        Resets the game.

        The parameters match those used during initialization.

        :param secret_word: The word the player is trying to guess.
        :param max_attempts: The maximum number of attempts the player has to
            guess the secret word. If this is a negative number, then the
            player will have an unlimited number of attempts.
        :param args: Other positional arguments.
        :param kwargs: Other keyword arguments.
        """
        raise NotImplementedError

    def is_unplayable(self,
                      *args: Any,
                      **kwargs: Any) -> WordleError | None:
        """
        If the simulator is unplayable in its current state.

        A :class:`NoAttemptsError` is returned if the game was terminated; the
        secret word has been guessed; or there are no more attempts left.
        """
        raise NotImplementedError

    def attempt_guess(self,
                      guess: str,
                      *args: Any,
                      **kwargs: Any) -> TileString:
        """
        Attempts to guess the secret word.

        The method generates a string of tiles after a guess, with each tile
        representing a character. The tiles are color-coded to indicate its
        accuracy in relation to the secret word. These hints should help the
        player deduce the secret word.

        ==========   ===================================================
          Color      Description
        ==========   ===================================================
        ``GRAY``     The character is not in the word at all.
        ``YELLOW``   The character is correct but in the wrong position.
        ``GREEN``    The character and its position are both correct.
        ==========   ===================================================

        :param guess: The guess the player made.

        :return: A string of tiles representing the accuracy of the guess.

        :raises NoAttemptsError: The game was terminated; the player has
            already guessed the secret word; or the player has no more attempts
            left.
        """
        raise NotImplementedError

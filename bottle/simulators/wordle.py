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
from collections import Counter
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

    :cvar BLACK: The character has not been used in a guess yet.
    :cvar GRAY: The character is not in the word at all.
    :cvar YELLOW: The character is correct but in the wrong position.
    :cvar GREEN: The character and its position are both correct.
    """
    BLACK = 0
    GRAY = 1
    YELLOW = 2
    GREEN = 3


class Tile:
    """
    A tile represents a character in a Wordle game, where each tile is assigned
    a hint on the character's accuracy.

    :ivar char: The character this tile represents.
    :ivar hint: The hint indicating the accuracy of this tile.
    """

    def __init__(self,
                 char: str,
                 hint: Hint = Hint.BLACK) -> None:
        """
        Initializes a tile object representing the given character.

        :param char: The character this tile represents.
        :param hint: The hint indicating the accuracy of the character this
            tile represents. Defaults to :class:`Hint.BLACK` indicating that
            the character has not been used yet.
        """
        self.char = char
        self.hint = hint


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

    :ivar _secret_word: The word the player is trying to guess.
    :ivar _max_attempts: The maximum number of attempts the player has to guess
        the secret word. If this is a negative number, then the player will
        have an unlimited number of attempts.
    :ivar _attempts_used: The number of attempts the player has used.
    :ivar _has_guessed_word: If the player has guessed the secret word.
    :ivar _is_terminated: If the game has been terminated.
    :ivar _ignore_case: The case sensitivity behavior for the simulator.
    """

    def __init__(self,
                 secret_word: str,
                 max_attempts: int = -1) -> None:
        """
        Initializes a Wordle simulator.

        :param secret_word: The word the player is trying to guess.
        :param max_attempts: The maximum number of attempts the player has to
            guess the secret word. If this is a negative number, then the
            player will have an unlimited number of attempts. Defaults to -1.
        """
        self._secret_word = secret_word
        self._max_attempts = max_attempts

        self._attempts_used = 0
        self._has_guessed_word = False
        self._is_terminated = False

        self._ignore_case = False

    @property
    def secret_word(self) -> str:
        """The word the player is trying to guess."""
        return self._secret_word

    @secret_word.setter
    def secret_word(self, secret_word: str) -> None:
        """
        Sets the secret word.

        :param secret_word: The secret word to change to.

        :raise WordleError: Setter is called during the middle of a game.
        """
        if self._attempts_used > 0 and self.has_attempts_left():
            raise WordleError(
                "changing the secret word in the middle of a game"
            )
        self._secret_word = secret_word

    @property
    def max_attempts(self) -> int:
        """
        The maximum number of attempts the player has to guess the secret word.
        If this is a negative number, then the player will have an unlimited
        number of guesses.
        """
        return self._max_attempts

    @max_attempts.setter
    def max_attempts(self, value: Any) -> None:
        """
        Sets the maximum number of attempts.

        :param value: The maximum number of attempts the player has to guess
            the secret word. If this is a negative number, then the player will
            have an unlimited number of guesses.

        :raise TypeError: ``value`` is not an integer.
        :raise WordleError: Setter is called during the middle of a game.
        """
        if not isinstance(value, int):
            raise TypeError("value is not an integer")
        if self._attempts_used > 0 and self.has_attempts_left():
            raise WordleError(
                "changing the maximum attempts in the middle of a game"
            )
        self._max_attempts = value

    @property
    def attempts_used(self) -> int:
        """The number of attempts the player has used."""
        return self._attempts_used

    def has_attempts_left(self) -> bool:
        """If the player can make another attempt at a guess."""
        if self._has_guessed_word or self._is_terminated:
            return False
        if self._max_attempts < 0:
            return True
        return self._attempts_used < self._max_attempts

    def has_guessed_word(self) -> bool:
        """If the player has guessed the secret word."""
        return self._has_guessed_word

    def terminate(self, flag: bool = True) -> None:
        """Quits the game."""
        self._is_terminated = flag

    def is_terminated(self) -> bool:
        """If the game has been terminated."""
        return self._is_terminated

    @property
    def ignore_case(self) -> bool:
        """The case sensitivity behavior for the simulator."""
        return self._ignore_case

    @ignore_case.setter
    def ignore_case(self, flag: Any) -> None:
        """
        Sets the case sensitivity behavior for the simulator.

        This method controls whether the simulator should perform operations in
        a case-sensitive manner. If the ``flag`` is true, the simulator will be
        case-insensitive. If the ``flag`` is false, the simulator will be
        case-sensitive.

        :param flag: A boolean flag to control case sensitivity. If true,
            operations will be case-insensitive. If false, operations will be
            case-sensitive.

        :raise TypeError: ``flag`` is not a boolean.
        :raise WordleError: Called during the middle of a game.
        """
        if not isinstance(flag, bool):
            raise TypeError("flag is not a boolean")
        if self._attempts_used > 0 and self.has_attempts_left():
            raise WordleError(
                "changing case sensitivity in the middle of a game"
            )
        self._ignore_case = flag

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
        self._secret_word = secret_word or self._secret_word
        self._max_attempts = max_attempts or self._max_attempts

        self._attempts_used = 0
        self._has_guessed_word = False
        self._is_terminated = False

    def is_unplayable(self,
                      *args: Any,
                      **kwargs: Any) -> WordleError | None:
        """
        If the simulator is unplayable in its current state.

        A :class:`NoAttemptsError` is returned if the game was terminated; the
        secret word has been guessed; or there are no more attempts left.
        """
        if self._is_terminated:
            return NoAttemptsError("The game was terminated")

        if self._has_guessed_word:
            return NoAttemptsError("Already guessed the secret word")

        if self._attempts_used == self._max_attempts:
            return NoAttemptsError("No attempts remaining")

        return None

    def generate_tile_string(self, string: str) -> TileString:
        """
        Generates a tile string for the given string.

        Each tile represent a character and are color-coded to indicate its
        accuracy in relation to the secret word.

        ==========   ===================================================
          Color      Description
        ==========   ===================================================
        ``GRAY``     The character is not in the word at all.
        ``YELLOW``   The character is correct but in the wrong position.
        ``GREEN``    The character and its position are both correct.
        ==========   ===================================================

        :param string: The string to compare the secret word with.

        :return: A string of tiles representing the accuracy of the guess.
        """
        secret_word = self._secret_word
        if self._ignore_case:
            secret_word = secret_word.upper()
            string = string.upper()

        counter = Counter()
        tiles = [Tile(char, Hint.GRAY) for char in string]

        min_length = min(len(string), len(secret_word))

        for i in range(min_length):
            if string[i] == (char := secret_word[i]):
                tiles[i].hint = Hint.GREEN
            else:
                counter[char] += 1

        for i in range(len(string)):
            if tiles[i].hint != Hint.GRAY:
                continue
            if counter[char := string[i]] > 0:
                tiles[i].hint = Hint.YELLOW
                counter[char] -= 1

        return TileString(tiles)

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
        if error := self.is_unplayable(*args, **kwargs):
            raise error

        tile_string = self.generate_tile_string(guess)
        self._has_guessed_word = True

        for tile in tile_string:
            if tile.hint != Hint.GREEN:
                self._has_guessed_word = False
                break

        self._attempts_used += 1
        return tile_string

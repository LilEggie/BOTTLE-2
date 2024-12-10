"""
The New York Times Wordle game and its components.

The objective of the game involves figuring out a secret word. The player's goal
is to guess this secret word in as few attempts as possible by using the
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

__all__ = ["Script", "Lexicon", "InvalidGuessError", "NYTWordleSimulator"]
__version__ = "1.0.0"
__author__ = "Eggie"


from typing import Iterable, Iterator

from bottle.simulators.wordle import TileString, WordleError, WordleSimulator


class Script:
    """
    Defines the character sets for different scripts supported by the
    :class:`NYTWordleSimulator`.
    """
    pass


class Lexicon:
    """
    A set of words implemented using a Trie data structure.

    This class provides efficient storage and retrieval of words, supporting
    operations such as adding, case-sensitive and case-insensitive search, and
    auto suggestions based on prefixes.
    """

    def __init__(self) -> None:
        """Initializes a lexicon using a Trie"""
        raise NotImplementedError

    def __len__(self) -> int:
        """The number of words in the lexicon."""
        raise NotImplementedError

    def add(self, word: str) -> None:
        """
        Adds a word to the Trie.

        This method inserts the specified word into the Trie by inserting each
        character of the word as a node in the Trie. If the word already
        exists, this method has no effect.

        :param word: The word to add to the Trie.
        """
        raise NotImplementedError

    def find(self,
             word: str,
             *,
             ignore_case: bool = False) -> bool:
        """
        Searches for a word in the Trie.

        This method searches for a specified word in the Trie. The search can
        be case-sensitive or case-insensitive based on the ``ignore_case``
        flag.

        :param word: The word to search for in the Trie.
        :param ignore_case: Whether to ignore case during the search. Defaults
            to false.

        :return: ``True`` if the word was found; ``False`` otherwise.
        """
        raise NotImplementedError

    def remove(self, word: str) -> None:
        """
        Removes a word from the Trie.

        This method removes a word from the Trie by traversing the Trie and
        cleaning up unused nodes. It does this with recursion. If the word
        does not exist, this method has no effect.

        :param word: The word to remove from the Trie.
        """
        raise NotImplementedError

    def autosuggest(self,
                    prefix: str,
                    *,
                    ignore_case: bool = False) -> set[str]:
        """
        Suggests words that begin with the given prefix.

        This method returns a set of words from the Trie that start with the
        specified prefix. The search can be case-sensitive or case-insensitive
        based on the ``ignore_case`` flag. If ``ignore_case`` is true, both
        lowercase and uppercase variants of the prefix are considered. The
        results are returned as a set to avoid duplicates.

        :param prefix: The prefix to search for in the Trie.
        :param ignore_case: Whether to ignore case during the search. Defaults
            to false.

        :return: A set of words that start with the given prefix.
        """
        raise NotImplementedError


class InvalidGuessError(WordleError):
    """An invalid guess was played."""
    pass


class NYTWordleSimulator(WordleSimulator):
    """
    A New York Times Wordle simulator.
    """

    def __init__(self,
                 secret_word: str = "",
                 max_attempts: int = 6) -> None:
        """
        Initializes a New York Times Wordle simulator.

        The simulator will use the default script and lexicon used by all New
        York Times Wordle.

        :param secret_word: The word the player is trying to guess.
        :param max_attempts: The maximum number of attempts the player has to
            guess the secret word. If this is a negative number, then the
            player will have an unlimited number of attempts. Defaults to -1.
        """
        raise NotImplementedError

    def add_script(self, char_collection: Iterable[str]) -> None:
        """
        Adds characters to the script.

        This method adds each character in the given collection to the
        internal ``_script`` set. It only adds characters that are exactly one
        character long.

        ``_script`` will no longer be none when this method is called. If that
        happens, this simulator will no longer use the default script used by
        all NYT Wordle games.

        :param char_collection: An iterable of characters to add to the script.

        :raise WordleError: Called during the middle of a game.
        """
        raise NotImplementedError

    def remove_script(self, char_collection: Iterable[str]) -> None:
        """
        Removes characters from the script.

        This method removes each character in the given collection from the
        internal ``_script`` set.

        :param char_collection: An iterable of characters to remove from the
            script.

        :raise WordleError: Called during the middle of a game.
        :raise RuntimeError: :meth:`add_script` was never called.
        """
        raise NotImplementedError

    def clear_script(self) -> None:
        """
        Clears all characters from the script.

        This method clears from the internal ``_script`` set.

        :raise WordleError: Called during the middle of a game.
        :raise RuntimeError: :meth:`add_script` was never called.
        """
        raise NotImplementedError

    def add_lexicon(self, word_collection: Iterable[str]) -> None:
        """
        Adds words to the lexicon.

        This method adds each word in the given collection to the internal
        ``_lexicon`` Trie.

        ``_lexicon`` will no longer be none when this method is called. If that
        happens, this simulator will no longer use the default lexicon used by
        all NYT Wordle games.

        :param word_collection: An iterable of words to add to the lexicon.

        :raise WordleError: Called during the middle of a game.
        """
        raise NotImplementedError

    def remove_lexicon(self, word_collection: Iterable[str]) -> None:
        """
        Removes words from the lexicon.

        This method removes each word in the given collection from the
        internal ``_lexicon`` Trie.

        :param word_collection: An iterable of words to remove from the
            lexicon.

        :raise WordleError: Called during the middle of a game.
        :raise RuntimeError: :meth:`add_lexicon` was never called.
        """
        raise NotImplementedError

    def clear_lexicon(self) -> None:
        """
        Clears all words from the lexicon.

        This method clears from the internal ``_lexicon`` Trie.

        :raise WordleError: Called during the middle of a game.
        :raise RuntimeError: :meth:`add_lexicon` was never called.
        """
        raise NotImplementedError

    def guess_history(self) -> Iterator[TileString]:
        """Returns an iterator of all the guesses the player made."""
        raise NotImplementedError

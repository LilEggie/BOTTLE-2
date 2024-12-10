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

__all__ = [
    "Script", "Lexicon", "lexicon", "word_list", "InvalidGuessError",
    "NYTWordleSimulator"
]
__version__ = "1.0.0"
__author__ = "Eggie"


import random
from typing import Any, Iterable, Iterator, Optional

import bottle.dir
import bottle.simulators.utils as utils
from bottle.simulators.wordle import TileString, WordleError, WordleSimulator


class Script:
    """
    Defines the character sets for different scripts supported by the
    :class:`NYTWordleSimulator`.

    :cvar ENGLISH_LOWERCASE: A set containing all lowercase English alphabetic
        characters.
    :cvar ENGLISH_UPPERCASE: A set containing all uppercase English alphabetic
        characters.
    :cvar ENGLISH: A combined set of both lowercase and uppercase English
        alphabetic characters.
    """
    ENGLISH_LOWERCASE = set("abcdefghijklmnopqrstuvwxyz")
    ENGLISH_UPPERCASE = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    ENGLISH = ENGLISH_LOWERCASE | ENGLISH_UPPERCASE


class _TrieNode:
    def __init__(self):
        self.children: dict[str, _TrieNode] = {}
        self.is_terminal = False


class Lexicon:
    """
    A set of words implemented using a Trie data structure.

    This class provides efficient storage and retrieval of words, supporting
    operations such as adding, case-sensitive and case-insensitive search, and
    auto suggestions based on prefixes.

    :ivar _root: The root of this Trie data structure.
    :ivar _size: The number of words in the lexicon.
    """

    def __init__(self) -> None:
        """Initializes a lexicon using a Trie"""
        self._root = _TrieNode()
        self._size = 0

    def __len__(self) -> int:
        """The number of words in the lexicon."""
        return self._size

    def add(self, word: str) -> None:
        """
        Adds a word to the Trie.

        This method inserts the specified word into the Trie by inserting each
        character of the word as a node in the Trie. If the word already
        exists, this method has no effect.

        :param word: The word to add to the Trie.
        """
        node = self._root
        for char in word:
            if char not in node.children:
                node.children[char] = _TrieNode()
            node = node.children[char]

        if not node.is_terminal:
            node.is_terminal = True
            self._size += 1

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
        if ignore_case:
            return self.__find_ignoring_case(word)

        node = self._root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_terminal

    def __find_ignoring_case(self, word: str) -> bool:
        """
        A helper method to search for a word in the Trie, ignoring case
        sensitivity.

        This method traverses the Trie to find all nodes with the ``word`` as
        their value, ignoring case sensitivity. If any one of these nodes is an
        end to a word, the method returns true.

        :return: ``True`` if the word was found; ``False`` otherwise.
        """
        self.__find_nodes_ignoring_case(self._root, word, 0, nodes := [])
        for n in nodes:
            if n.is_terminal:
                return True
        return False

    @staticmethod
    def __find_nodes_ignoring_case(node: _TrieNode,
                                   word: str,
                                   depth: int,
                                   nodes_found: list[_TrieNode]) -> None:
        """
        A helper method to find all the nodes that have the value ``word``,
        ignoring case sensitivity.

        This method traverses the Trie starting from the given node, usually
        from the root, matching characters in the word at the current depth. It
        checks for both lowercase and uppercase versions of each character. If
        matching nodes are found, they are added to the list.

        This function is used for :meth:`find` and :meth:`autosuggest`.

        :param node: The current node being processed.
        :param word: The word being searched for in the Trie.
        :param depth: The current depth in the word, indicating the character
            being processed.
        :param nodes_found: A list to store nodes having the ``word`` as their
            value.
        """
        if depth == len(word):
            nodes_found.append(node)
            return

        upper = word[depth].upper()
        lower = upper.lower()

        if upper in node.children:
            Lexicon.__find_nodes_ignoring_case(
                node.children[upper], word, depth + 1, nodes_found
            )
        if lower in node.children:
            Lexicon.__find_nodes_ignoring_case(
                node.children[lower], word, depth + 1, nodes_found
            )

    def remove(self, word: str) -> None:
        """
        Removes a word from the Trie.

        This method removes a word from the Trie by traversing the Trie and
        cleaning up unused nodes. It does this with recursion. If the word
        does not exist, this method has no effect.

        :param word: The word to remove from the Trie.
        """
        self.__remove(self._root, word, 0)

    def __remove(self,
                 node: _TrieNode,
                 word: str,
                 depth: int) -> bool:
        """
        A helper method to remove a word from the Trie.

        This method traverses the Trie starting from the given node, usually
        from the root, matching characters in the word at the current depth. If
        a matching node is found, it is removed from the Trie. If there are
        nodes that no longer belong to a word, they will be deleted.

        :param node: The current node being processed.
        :param word: The word to remove from the Trie.
        :param depth: The current depth in the word, indicating the character
            being processed.

        :return: ``True`` if the current node can be safely deleted; ``False``
            otherwise.
        """
        if not node:
            return False

        if depth == len(word):
            if node.is_terminal:
                node.is_terminal = False
                self._size -= 1
                return len(node.children) == 0
            return False

        if (char := word[depth]) not in node.children:
            return False

        remove_child = self.__remove(node.children[char], word, depth + 1)
        if remove_child:
            del node.children[char]
            return len(node.children) == 0 and not node.is_terminal
        return False

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
        if ignore_case:
            return self.__auto_suggest_ignoring_case(prefix)

        node = self._root
        for char in prefix:
            if char not in node.children:
                return set()
            node = node.children[char]

        self.__auto_suggest(node, prefix, suggestions := set())
        return suggestions

    def __auto_suggest_ignoring_case(self, prefix: str) -> set[str]:
        """
        A helper method to search for words that begin with the given prefix,
        ignoring case.

        This method finds all nodes that have the ``prefix`` as their value,
        regardless of case. It traverses through each found node for words,
        which are added as suggestive words. A set of words is returned,
        ensuring that duplicates are removed.

        :param prefix: The prefix to search for in the Trie.

        :return: A set of words that start with the given prefix, ignoring
            case.
        """
        self.__find_nodes_ignoring_case(self._root, prefix, 0, nodes := [])
        suggestions = set()
        for n in nodes:
            self.__auto_suggest(n, prefix, s := set(), ignore_case=True)
            suggestions.update(s)
        return suggestions

    @staticmethod
    def __auto_suggest(node: _TrieNode,
                       prefix: str,
                       suggestions: set[str],
                       *,
                       ignore_case: bool = False) -> None:
        """
        A helper method to search for words that begin with the given prefix.

        This method traverses the Trie from the given node to find all words
        that begin with the specified prefix. These words are collected and
        returned as a set to ensure that duplicates are removed. Ignoring case
        will further remove duplicate words.

        :param node: The current node being processed.
        :param prefix: The prefix to search for in the Trie.
        :param suggestions: A set to store words that match the given prefix.
        :param ignore_case: Whether to ignore case when searching for words.
            Defaults to false.
        :return:
        """
        if node.is_terminal:
            suggestions.add(prefix)
        for char, child in node.children.items():
            if ignore_case:
                char = char.lower()
            Lexicon.__auto_suggest(
                child, prefix + char, suggestions,
                ignore_case=ignore_case
            )


__filepath = bottle.dir.resources / "wordle" / "nyt"

lexicon = Lexicon()
"""The lexicon all NYT Wordle games use."""
for __word in utils.extract_words(__filepath / "lexicon.txt"):
    lexicon.add(__word)

word_list = list(utils.extract_words(__filepath / "word_list.txt"))
"""The word list NYT Wordle uses for generating random words."""


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
        secret_word = secret_word or random.choice(word_list)
        super().__init__(secret_word, max_attempts)

        self._script: Optional[set[str]] = None
        self._lexicon: Optional[Lexicon] = None

        self._guess_history: list[TileString] = []

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
        if self._attempts_used > 0 and self.has_attempts_left():
            raise WordleError(
                "changing the script contents in the middle of a game"
            )
        if self._script is None:
            self._script = set()
        for s in char_collection:
            if len(s) == 1:
                self._script.add(s)

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
        if self._attempts_used > 0 and self.has_attempts_left():
            raise WordleError(
                "changing the script contents in the middle of a game"
            )
        if self._script is None:
            raise RuntimeError("removing from a script that does not exist")
        self._script.difference_update(char_collection)

    def clear_script(self) -> None:
        """
        Clears all characters from the script.

        This method clears from the internal ``_script`` set.

        :raise WordleError: Called during the middle of a game.
        :raise RuntimeError: :meth:`add_script` was never called.
        """
        if self._attempts_used > 0 and self.has_attempts_left():
            raise WordleError(
                "changing the script contents in the middle of a game"
            )
        if self._script is None:
            raise RuntimeError("clearing a script that does not exist")
        self._script.clear()

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
        if self._attempts_used > 0 and self.has_attempts_left():
            raise WordleError(
                "changing the lexicon contents in the middle of a game"
            )
        if self._lexicon is None:
            self._lexicon = Lexicon()
        for word in word_collection:
            self._lexicon.add(word)

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
        if self._attempts_used > 0 and self.has_attempts_left():
            raise WordleError(
                "changing the lexicon contents in the middle of a game"
            )
        if self._lexicon is None:
            raise RuntimeError("removing from a lexicon that does not exist")
        for word in word_collection:
            self._lexicon.remove(word)

    def clear_lexicon(self) -> None:
        """
        Clears all words from the lexicon.

        This method clears from the internal ``_lexicon`` Trie.

        :raise WordleError: Called during the middle of a game.
        :raise RuntimeError: :meth:`add_lexicon` was never called.
        """
        if self._attempts_used > 0 and self.has_attempts_left():
            raise WordleError(
                "changing the lexicon contents in the middle of a game"
            )
        if self._lexicon is None:
            raise RuntimeError("clearing a lexicon that does not exist")
        self._lexicon = Lexicon()

    def guess_history(self) -> Iterator[TileString]:
        """Returns an iterator of all the guesses the player made."""
        return iter(self._guess_history)

    def is_unplayable(self,
                      *args: Any,
                      **kwargs: Any) -> WordleError | None:
        """
        If the simulator is unplayable in its current state.

        A :class:`NoAttemptsError` is returned if the game was terminated; the
        secret word has been guessed; or there are no more attempts left.

        An :class:`InvalidGuessError` is returned if the guess is shorter or
        longer than the secret word; the guess contains invalid characters; or
        the guess is not a valid word.

        Characters are valid if they are in the script this simulator is using.
        If the script is empty, any character is valid. If no script exist, the
        default script will be used.

        Words are valid if they are in the lexicon this simulator is using. If
        the lexicon is empty, any word is valid. If no lexicon exists, the
        default lexicon will be used.

        :raise TypeError: If the value of "guess" or the first argument is not a
            string.
        """
        if error := super().is_unplayable():
            return error

        guess = kwargs.get("guess", args[0] if args else None)
        if guess is None:
            return None
        if not isinstance(guess, str):
            raise TypeError(
                'value of "guess" must be a string, or the first argument must'
                ' be a string'
            )

        length_diff = len(guess) - len(self._secret_word)
        if length_diff != 0:
            adjective = "short" if length_diff < 0 else "long"
            return InvalidGuessError("Guess is too " + adjective)

        script = self._script or Script.ENGLISH
        for char in guess:
            if len(script) == 0:
                break
            check_chars = {char}
            if self._ignore_case:
                check_chars.update(char.lower() + char.upper())
            if not any(c in script for c in check_chars):
                return InvalidGuessError("Guess contains invalid characters")

        __lexicon = self._lexicon or lexicon
        if len(__lexicon) == 0:
            return
        if not __lexicon.find(guess, ignore_case=self._ignore_case):
            return InvalidGuessError("Guess is not a word")

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

        :raise NoAttemptsError: The game was terminated; the player has
            already guessed the secret word; or the player has no more attempts
            left.
        :raise InvalidGuessError: The guess is shorter or longer than the
            secret word; the guess contains invalid characters; or the guess is
            not in the lexicon.
        """
        tile_string = super().attempt_guess(guess, guess)
        self._guess_history.append(tile_string)
        return tile_string

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

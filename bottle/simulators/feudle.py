"""
The Feudle game and its components.

The objective of the game involves figuring out the missing secret word in a
sentence. The player's goal is to guess this secret word in as few attempts as
possible by using the color-coded hints the game provides.

==========   ===================================================
  Color      Description
==========   ===================================================
``BLACK``    The character has not been used in a guess yet.
``GRAY``     The character is not in the word at all.
``YELLOW``   The character is correct but in the wrong position.
``GREEN``    The character and its position are both correct.
==========   ===================================================
"""

__all__ = ["lexicon", "sentence_list", "word_list", "FeudleSimulator"]
__version__ = "1.0.0"
__author__ = "Eggie"


import json
import random
import re
from typing import Any, Optional

import bottle.dir
import bottle.simulators.utils as utils
from bottle.simulators.nyt import Lexicon, NYTWordleSimulator


__filepath = bottle.dir.resources / "wordle" / "feudle"

lexicon = Lexicon()
"""The lexicon all Feudle games use."""
for __word in utils.extract_words(__filepath / "lexicon.txt"):
    lexicon.add(__word)

with open(__filepath / "sentence_list.json") as __file:
    sentence_list: dict[str, list[str]] = json.load(__file)
    """The sentences Feudle uses for every word in the word list."""

word_list = list(sentence_list)
"""The word list Feudle uses for generating random words."""


class FeudleSimulator(NYTWordleSimulator):
    """
    A Feudle simulator.
    """

    def __init__(self,
                 secret_word: str = "",
                 max_attempts: int = 6,
                 *,
                 sentence: str = "") -> None:
        """
        Initializes a Feudle simulator.

        The simulator will use the default script and lexicon used by all
        Feudles.

        :param secret_word: The word the player is trying to guess.
        :param max_attempts: The maximum number of attempts the player has to
            guess the secret word. If this is a negative number, then the
            player will have an unlimited number of attempts. Defaults to -1.
        :param sentence: The sentence the simulator will use. Must contain the
            secret word.
        """
        secret_word = secret_word or random.choice(word_list)
        super().__init__(secret_word, max_attempts)

        self._sentence = sentence or random.choice(sentence_list[secret_word])
        self._sentence_without_word = re.sub(
            fr"\b{re.escape(secret_word)}\b",
            "**[blank]**",
            self._sentence,
            flags=re.IGNORECASE
        )

    @property
    def sentence(self) -> str:
        """The sentence the simulator is using."""
        return self._sentence

    @property
    def sentence_without_word(self) -> str:
        """The sentence the simulator is using, excluding the secret word."""
        return self._sentence_without_word

    def reset(self,
              secret_word: Optional[str] = None,
              max_attempts: Optional[int] = None,
              *args: Any,
              **kwargs: Any) -> None:
        """
        Resets the game with a new secret word.

        The parameters match those used during initialization.

        >>> feudle = FeudleSimulator("word", 6, sentence="my sentence")
        >>> feudle.reset("word", 6, sentence="another sentence")
        >>> feudle.reset(sentence="cool sentence")

        :param secret_word: The word the player is trying to guess.
        :param max_attempts: The maximum number of attempts the player has to
            guess the secret word. If this is a non-positive number, then the
            player has an unlimited amount of attempts.
        """
        super().reset(secret_word, max_attempts, *args, **kwargs)
        if "sentence" in kwargs:
            self._sentence = kwargs["sentence"]
        else:
            self._sentence = random.choice(sentence_list[self._secret_word])

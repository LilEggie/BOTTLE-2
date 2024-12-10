"""
Abstract class for Discord games.
"""

__all__ = ["DiscordGame"]
__version__ = "1.0.0"
__author__ = "Eggie"


import time
import abc

import discord


class DiscordGame(abc.ABC):
    """
    A game the client will have for its players.

    A Discord game keeps track of time—when the game has started and ended, and
    how much time elapsed since the game started.

    A Discord game is also runnable.
    """

    def __init__(self,
                 interaction: discord.Interaction,
                 room: discord.Thread) -> None:
        """
        Initializes a playable Discord game.

        :param interaction: The Discord interaction.
        :param room: The thread the Discord game will be in.
        """
        self._interaction = interaction
        self._user = interaction.user
        self._room = room

        self._start_time = -1.0
        self._end_time = -1.0

    def has_started(self) -> bool:
        """Whether the game has started."""
        return self._start_time >= 0

    def has_ended(self) -> bool:
        """Whether the game has ended."""
        return self._end_time >= 0

    def start_timer(self) -> None:
        """
        Starts the timer.

        :raise RuntimeError: The timer has already started.
        """
        if self.has_started():
            raise RuntimeError("timer has already started")
        self._start_time = time.time()

    def end_timer(self) -> None:
        """
        Ends the timer.

        :raise RuntimeError: The timer has already ended.
        """
        if not self.has_started():
            raise RuntimeError("timer has not started yet")
        if self.has_ended():
            raise RuntimeError("timer has already ended")
        self._end_time = time.time()

    def reset_timer(self) -> None:
        """Resets the timer."""
        self._start_time = -1.0
        self._end_time = -1.0

    def time_elapsed(self) -> float:
        """
        Returns the time that has passed since the timer started.

        In an ideal game, the timer begins as soon as the game starts.

        If the timer has ended, the time from start to end will be returned. If
        the timer's still running, the time since the game started is returned.

        :raise RuntimeError: The timer has not started yet.
        """
        if not self.has_started():
            raise RuntimeError("timer has not started yet")
        if not self.has_ended():
            return time.time() - self._start_time
        return self._end_time - self._start_time

    @abc.abstractmethod
    async def run(self) -> None:
        """This is where the game starts and runs."""
        pass

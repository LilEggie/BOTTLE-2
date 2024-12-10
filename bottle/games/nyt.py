__all__ = ["NYTWordle"]
__version__ = "1.0.0"
__author__ = "Eggie"


from typing import Optional

import discord

import bottle.emoji as emoji
import bottle.logger
from bottle.games.abc import DiscordGame
from bottle.simulators import NYTWordleSimulator, WordleSimulator
from bottle.simulators.wordle import TileString
from bottle.simulators.nyt import InvalidGuessError


class NYTWordle(DiscordGame):
    def __init__(self,
                 interaction: discord.Interaction,
                 room: discord.Thread) -> None:
        super().__init__(interaction, room)

        self.title = "NYT Wordle"
        self.color = discord.Color.yellow()

        self._wordle: Optional[WordleSimulator] = None

    async def run(self) -> None:
        wordle = self._wordle or NYTWordleSimulator()
        wordle.ignore_case = True

        game_embed = self._create_game_embed(wordle)
        game_message = await self._room.send(embed=game_embed)

        game_logger = bottle.logger.get_logger("bottle.game")
        game_logger.info(
            f"{self._user} started a {self.title} game ({wordle.secret_word})"
        )

        self.start_timer()

        while wordle.has_attempts_left():
            if not (guess := await self._wait_for_guess()):
                continue
            if not wordle.has_attempts_left():
                return

            await guess.delete()
            try:
                tile_string = wordle.attempt_guess(guess.content)
            except InvalidGuessError as e:
                embed = discord.Embed(
                    title="Invalid Guess",
                    description=str(e),
                    color=discord.Color.red()
                )
                await self._room.send(embed=embed, delete_after=5)
                continue

            self._update_game_embed(game_embed, wordle, tile_string)
            game_message = await game_message.edit(embed=game_embed)

        self.end_timer()

    def _create_game_embed(self, wordle: WordleSimulator) -> discord.Embed:
        embed = discord.Embed(title=self.title, color=self.color)
        embed.set_author(name=self._user.display_name)

        blank_word = emoji.get_tile_code(None) * len(wordle.secret_word)
        for _ in range(wordle.max_attempts):
            embed.add_field(name="", value=blank_word, inline=False)
        return embed

    @staticmethod
    def _update_game_embed(game_embed: discord.Embed,
                           wordle: WordleSimulator,
                           tile_string: TileString) -> None:
        game_embed.set_field_at(
            index=wordle.attempts_used - 1,
            name="",
            value="".join(emoji.get_tile_code(tile) for tile in tile_string),
            inline=False
        )

        if wordle.has_guessed_word():
            game_embed.colour = discord.Color.green()
        elif not wordle.has_attempts_left():
            game_embed.colour = discord.Color.red()

    async def _wait_for_guess(self) -> discord.Message | None:
        def check(message: discord.Message) -> discord.Message | None:
            if message.author.id != self._user.id:
                return
            if message.channel.id == self._room.id:
                return message

        return await self._interaction.client.wait_for("message", check=check)  # noqa

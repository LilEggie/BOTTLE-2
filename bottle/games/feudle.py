__all__ = ["Feudle"]
__version__ = "1.0.0"
__author__ = "Eggie"


import discord

from bottle.games.nyt import NYTWordle
from bottle.simulators import FeudleSimulator


class Feudle(NYTWordle):
    def __init__(self,
                 interaction: discord.Interaction,
                 room: discord.Thread) -> None:
        super().__init__(interaction, room)
        self.title = "Feudle"

    async def run(self) -> None:
        self._wordle = FeudleSimulator()
        embed = discord.Embed(
            title="",
            description=self._wordle.sentence_without_word,
            color=discord.Color.greyple()
        )
        await self._room.send(embed=embed)
        await super().run()

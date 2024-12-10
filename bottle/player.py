"""
This module caches player data.
"""


__all__ = ["get_room", "search_room", "create_room"]
__version__ = "1.0.0"
__author__ = "Eggie"


from typing import Optional

import discord

import bottle.logger


logger = bottle.logger.get_logger("bottle.player")

__rooms: dict[int, discord.Thread]
__rooms = {}

Player = discord.Member | discord.User
Channel = discord.TextChannel | discord.Thread


async def get_room(user: Player,
                   guild: discord.Guild,
                   channel: Channel) -> discord.Thread:
    """
    Gets the player's room.

    The returned room will be cached.

    :param user: The Discord user.
    :param guild: The guild to search the room in.
    :param channel: The channel to create the room if it doesn't exist.

    :return: The thread that belongs to the user.
    """
    cache = __rooms
    if room := cache.get(user.id):
        return room

    if room := await search_room(user, guild):
        cache[user.id] = room
        return room

    return await create_room(user, channel)


def __room_name(user: Player) -> str:
    """The name of the user's room."""
    return f"{user.name.capitalize()}'s Room"


async def search_room(user: Player,
                      guild: discord.Guild) -> discord.Thread | None:
    """
    Searches for the user's room.

    :param user: The Discord user.
    :param guild: The guild to search in.

    :return: The thread that belongs to the user. Returns none if their room
        doesn't exist.
    """
    cache = __rooms
    if (room := cache.get(user.id)) and room.guild.id == guild.id:
        return room

    room_name = __room_name(user)

    for room in guild.threads:
        if room.name == room_name:
            cache[user.id] = room
            return room

    for channel in guild.channels:
        if not isinstance(channel, discord.TextChannel):
            continue
        async for room in channel.archived_threads(private=True):
            if room.name == room_name:
                cache[user.id] = room
                return room
        async for room in channel.archived_threads(private=False):
            if room.name == room_name:
                cache[user.id] = room
                return room

    return None


async def create_room(user: Player,
                      channel: Channel,
                      *,
                      private: bool = True,
                      invitable: bool = True,
                      auto_archive_duration: int = 60,
                      slowmode_delay: int = 0) -> discord.Thread:
    """
    Creates a room for the user.

    This will create a room regardless if the user already has one or not.

    :param user: The Discord user.
    :param channel: The channel where the created room will be. If the channel
        is a thread, then wherever the thread is located will be the new
        channel. The created thread will be in that channel instead.
    :param private: If the room is accessible only by the user and moderators.
        Defaults to true.
    :param invitable: If other users can be invited to the room. Defaults to
        true.
    :param auto_archive_duration: The time in minutes for the room to be
        automatically archived. Defaults to 60 minutes.
    :param slowmode_delay: The delay in seconds between messages. Defaults to
        0 seconds.

    :return: The user's newly created room.

    :raise TypeError: ``channel`` must be a text channel or thread.
    """
    if isinstance(channel, discord.Thread):
        channel = channel.parent

    room_type = discord.ChannelType.public_thread
    if private:
        room_type = discord.ChannelType.private_thread

    room = await channel.create_thread(
        name=__room_name(user),
        type=room_type,
        invitable=invitable,
        auto_archive_duration=auto_archive_duration,
        slowmode_delay=slowmode_delay
    )

    if user.id in __rooms:
        logger.warning("Created a new room when user already had one")

    __rooms[user.id] = room
    return room


"""
This module is responsible for handling and managing Discord users.
"""

__all__ = [
    "get_discord_objects_from_json", "get_admins", "is_admin", "admins"
]
__version__ = "1.0.0"
__author__ = "Eggie"


import json
from typing import Optional, TextIO, Type

import discord

from bottle.definitions import RESOURCE_DIR


def get_discord_objects_from_json(
    file: TextIO,
    *,
    object_type: Optional[Type[discord.abc.Snowflake]] = None
) -> set[discord.Object]:
    """
    Returns a set of Discord objects from a JSON file.

    :param file: The JSON file to parse as a set of Discord objects.
    :param object_type:

    :return: The set of Discord objects from the parsed list in the JSON file.

    :raises ValueError: The JSON is not formatted as a list, or the parsed list
            contains a non-integer value.
    """
    data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("the JSON being parsed must be a list")

    objects = set()
    for uid in data:
        if not isinstance(uid, int):
            raise ValueError(f'expected an integer in JSON but found "{uid}"')
        objects.add(discord.Object(uid, type=object_type))

    return objects


def get_admins() -> set[discord.Object]:
    """
    Returns a set of admins in the form of Discord objects.

    ``admins.json`` will be created if it does not exist in the resource
    directory.

    :return: The set of Discord objects from the parsed list in the JSON file
             ``admins.json``.

    :raises ValueError: ``admin.json`` is not formatted as a list, or the
            parsed list contains a non-integer value.
    """
    filepath = RESOURCE_DIR / "admins.json"
    if created_file := not filepath.exists():
        filepath.touch()

    with open(filepath, "r+") as file:
        if created_file:
            json.dump([], file)
            file.seek(0)
        return get_discord_objects_from_json(file, object_type=discord.User)


def is_admin(user: discord.Member | discord.User) -> bool:
    """
    Logic for whether the provided user is an administrator.

    :param user: The user to check if they are an admin.

    :return: ``True`` if the user is an admin; ``False`` otherwise.
    """
    return user in admins


admins = get_admins()
"""
The Discord users who have access to every application command available.
"""

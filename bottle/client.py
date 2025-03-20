"""
The client that will be managing and running BOTTLE.
"""

__all__ = ["run"]
__version__ = "1.0.0"
__author__ = "Eggie"


import functools
import os
from typing import Optional

import discord
import discord.ext.commands
import dotenv

import bottle.user as user
from bottle.definitions import RESOURCE_DIR


def run() -> None:
    """
    Runs the client.
    """
    envfile = RESOURCE_DIR / ".env"
    if not envfile.is_file():
        raise FileNotFoundError(str(envfile))

    dotenv.load_dotenv(envfile)
    if not (token := os.getenv("TOKEN")):
        raise LookupError("TOKEN not found in " + str(envfile))

    client.run(token)


#------------------------------------------------------------------------------
#   Setup
#------------------------------------------------------------------------------


def disable_command_prefix(_, message: discord.Message) -> str:
    """
    Disables the command prefix functionality of the client by dynamically
    returning a prefix that is impossible for the user to type.

    The prefix is generated based on the first character of the message,
    preceded by an exclamation mark. If the message content is somehow empty, a
    default prefix of "!" is returned.

    :param _: This holds the client :class:`discord.ext.commands.Bot`. However,
           it is ignored and will not be used in this function.
    :param message: This is the user's :class:`discord.Message`.

    :return: A dynamically generated prefix string that starts with a "!" and
             ends with the first character of the message. However, if the
             message is somehow empty, a default prefix of "!" is returned.
    """
    # I highly doubt the message can be empty, but just in case.
    if len(s := message.content) == 0:
        return "!"
    return "!" + s[0]


client = discord.ext.commands.Bot(
    command_prefix=disable_command_prefix,   # noqa
    intents=discord.Intents.all()
)
"""
The client that handles Discord events and commands executed by the users.
"""


#------------------------------------------------------------------------------
#   Bot Events
#------------------------------------------------------------------------------


@client.event
async def on_connect() -> None:
    await client.change_presence(activity=discord.Game("Wordle"))


#------------------------------------------------------------------------------
#   Bot Commands
#------------------------------------------------------------------------------


class CommandMessage(object):
    """
    A resulting message after executing a command through the client.

    :ivar interaction: The interaction representing the user's action.
    :ivar embed: The message of this :class:`CommandMessage` is stored in a
          Discord embed.
    """

    def __init__(
        self,
        interaction: discord.Interaction,
        *,
        title: Optional[str] = None
    ) -> None:
        """
        Initializes a command message for the provided interaction.

        The initializer creates an :class:`discord.Embed` with the provided
        :param:`title`. This embed is colored gray.

        :param interaction: The interaction representing the user's action.
        :param title: The title of the message. Defaults to none.
        """
        self.interaction = interaction
        self.embed = discord.Embed(title=title, color=discord.Color.greyple())

    def add_message(self, context: str) -> None:
        """
        Adds context to the command message.

        :param context: The context to add to this message.

        :raises ValueError: The context exceeds 1024 characters in length.
        """
        if len(context) > 1024:
            raise ValueError("the context can only be 1024 characters long")

        self.embed.add_field(name="", value=context, inline=False)

    async def send_message(
        self,
        context: Optional[str] = None,
        *,
        color: Optional[discord.Color] = None
    ) -> None:
        """
        Sends the command message to Discord by using the provided interaction.

        :param context: The context to add to this command message. If this is
               none, nothing will be added. Defaults to none.
        :param color: The color the embed will be. If this is none, the embed
               color will remain the same. Defaults to none.

        :raises ValueError: The context exceeds 1024 characters in length.
        """
        if context:
            self.add_message(context)
        if color:
            self.embed.colour = color

        if self.interaction.response.is_done():   # noqa
            await self.interaction.edit_original_response(embed=self.embed)
        else:
            await self.interaction.response.send_message(   # noqa
                embed=self.embed,
                ephemeral=True
            )

    async def delete_message(self, *, delay: Optional[float] = None) -> None:
        """
        Deletes the command message from the Discord.

        :param delay: If provided, the number of seconds to wait in the
               background before deleting the message. If the deletion fails
               then it is silently ignored.

        :raises HTTPException: Fetching the original response message failed.
        :raises ClientException: The channel for the message could not be
                resolved.
        :raises NotFound: The interaction response message does not exist.
        """
        message = await self.interaction.original_response()
        await message.delete(delay=delay)

    async def info(self, context: str) -> None:
        """
        Adds an info message and sends it to Discord by using the provided
        interaction.

        The embed's color will be changed to gray.

        :param context: The context of the info message.

        :raises ValueError: The context exceeds 1024 characters in length.
        """
        await self.send_message(context, color=discord.Color.greyple())

    async def success(self, context: str) -> None:
        """
        Adds a success message and sends it to Discord by using the provided
        interaction.

        The embed's color will be changed to green.

        :param context: The context of the success message.

        :raises ValueError: The context exceeds 1024 characters in length.
        """
        await self.send_message(context, color=discord.Color.brand_green())

    async def error(self, context: str) -> None:
        """
        Adds an error message and sends it to the Discord by using the provided
        interaction.

        The embed's color will be changed to red.

        :param context: The context of the error message.

        :raises ValueError: The context exceeds 1024 characters in length.
        """
        await self.send_message(context, color=discord.Color.brand_red())


def requires_admin_perms(func):
    """
    A decorator to ensure that only users with admin permissions can execute
    the Discord command.

    :param func: The Discord command function.

    :return: The wrapped Discord command function.
    """
    @functools.wraps(func)
    async def wrapper(interaction: discord.Interaction, *args, **kwargs):
        if not user.is_admin(interaction.user):
            await interaction.response.send_message(   # noqa
                "You don't have the required permissions to use this command.",
                ephemeral=True,
                delete_after=10
            )
            return
        await func(interaction, *args, **kwargs)
    return wrapper


@client.tree.command(name="sync", description="Admins only.")
@requires_admin_perms
async def sync(interaction: discord.Interaction) -> None:
    """
    Syncs the application commands to Discord.

    This must be called for the application commands to show up.

    This requires administrator powers in order to use this command.

    Application commands should be manually synced to Discord to prevent the
    client from getting rate limited.

    :param interaction: The interaction representing the user's action.

    :raises HTTPException: Syncing the commands failed.
    :raises CommandSyncFailure: Syncing the commands failed due to a user
            related error, typically because the command has invalid data.
            This is equivalent to an HTTP status code of 400.
    :raises Forbidden: The client does not have the applications. commands
            scope in the guild.
    :raises MissingApplicationID: The client does not have an application ID.
    :raises TranslationError: An error occurred while translating the commands.
    """
    message = CommandMessage(interaction, title="Sync Commands Request")
    await message.info("...syncing global commands")

    try:
        await client.tree.sync()
        await message.success("Successfully fulfilled request.")
    except discord.app_commands.CommandSyncFailure as e:
        errmsg = ("Syncing the commands failed due to a user related error,"
                  " typically because the command has invalid data. This is"
                  " equivalent to an HTTP status code of 400.")
        await message.error(errmsg)
        raise e
    except discord.Forbidden as e:
        errmsg = ("The client does not have the application.commands scope in"
                  " the guild.")
        await message.error(errmsg)
        raise e
    except discord.app_commands.MissingApplicationID as e:
        errmsg = "The client does not have an application ID."
        await message.error(errmsg)
        raise e
    except discord.app_commands.TranslationError as e:
        errmsg = "An error occurred while translating the commands."
        await message.error(errmsg)
        raise e
    except discord.HTTPException as e:
        errmsg = "Syncing the commands failed."
        await message.error(errmsg)
        raise e

    await message.delete_message(delay=10)

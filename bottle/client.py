__all__ = ["run", "client"]
__version__ = "1.0.0"
__author__ = "Eggie"


import os

import discord
import discord.abc
import discord.app_commands
import discord.errors
import discord.ext.commands
import dotenv

import bottle.dir
import bottle.logger


def run() -> None:
    """Starts up the discord bot."""
    env_file = bottle.dir.resources / ".env"
    if not os.path.isfile(env_file):
        raise FileNotFoundError(str(env_file))

    dotenv.load_dotenv(env_file)
    token = os.getenv("TOKEN")

    if not token:
        raise LookupError(f"TOKEN not found in " + str(env_file))

    client.run(token)


#------------------------------------------------------------------------------
#   Setup
#------------------------------------------------------------------------------


admins = {}
guild_masters = []


__intents = discord.Intents.default()
__intents.guilds = True
__intents.members = True
__intents.message_content = True


client = discord.ext.commands.Bot(
    command_prefix="!",
    intents=__intents
)

logger = bottle.logger.get_logger("bottle.client")


#------------------------------------------------------------------------------
#   Bot Events
#------------------------------------------------------------------------------


@client.event
async def on_connect():
    logger.info(f"... connecting")


@client.event
async def on_disconnect():
    logger.info(f"... disconnecting")


@client.event
async def on_ready():
    try:
        logger.info("... syncing globally")
        await client.tree.sync()
        logger.info("... syncing guild masters")
        for guild in guild_masters:
            await client.tree.sync(guild=guild)
    except discord.app_commands.CommandSyncFailure as e:
        logger.critical(
            "Syncing the commands failed due to a user related error,"
            " typically because the command has invalid data. This is"
            " equivalent to an HTTP status code of 400.", exc_info=e
        )
        raise e
    except discord.Forbidden as e:
        logger.critical(
            "The client does not have the applications.commands scope in the"
            " guild.", exc_info=e
        )
        raise e
    except discord.app_commands.MissingApplicationID as e:
        logger.critical(
            "The client does not have an application ID.", exc_info=e
        )
        raise e
    except discord.app_commands.TranslationError as e:
        logger.critical(
            "An error occurred while translating the commands.", exc_info=e
        )
        raise e
    except discord.HTTPException as e:
        logger.critical("Syncing the commands failed.", exc_info=e)
        raise e

    logger.info("... changing activity")
    try:
        await client.change_presence(activity=discord.Game("Wordle"))
    except TypeError as e:
        logger.warning("Changing the client's activity failed.", exc_info=e)

    logger.info(f"{client.user} is ready")


#------------------------------------------------------------------------------
#   Bot Commands
#------------------------------------------------------------------------------


async def requires_admin_perms(interaction: discord.Interaction) -> None:
    if interaction.user.id in admins:
        return

    if cmd := interaction.command:
        await interaction.response.send_message(  # noqa
            f"Sorry, `/{cmd.name}` is currently unavailable",
            ephemeral=True,
            delete_after=10
        )
    else:
        await interaction.response.send_message(  # noqa
            f"Sorry, this is currently unavailable",
            ephemeral=True,
            delete_after=10
        )

    raise PermissionError(f"{interaction.user.name} is not an admin")


@client.tree.command(
    name="debug",
    description="For debugging purposes",
    guilds=guild_masters
)
async def debug(interaction: discord.Interaction):
    await requires_admin_perms(interaction)
    await interaction.response.send_message(  # noqa
        "hi",
        ephemeral=True,
        delete_after=0
    )


@client.tree.command(
    name="help",
    description="Displays available commands"
)
async def help(interaction: discord.Interaction):
    await requires_admin_perms(interaction)
    embed = discord.Embed(
        title="Help",
        description="List of all commands",
        color=discord.Color.greyple()
    )

    for slash_cmd in client.tree.walk_commands():
        embed.add_field(
            name=f"**/{slash_cmd.name}**",
            value=slash_cmd.description
        )

    await interaction.response.send_message(  # noqa
        embed=embed,
        ephemeral=True
    )

import discord
from discord.ext import commands
import asyncio

class SleepCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_sleeping = False
        self.wake_up_task = None

    @discord.app_commands.command(name="sleep", description="Make Blevitron ignore messages for a specified amount of time.")
    async def sleep(self, interaction: discord.Interaction, duration: int = None):
        """
        Make Blevitron ignore messages for a specified amount of time.
        Duration is specified in minutes. If no duration is provided, the bot will sleep indefinitely.
        """
        if self.is_sleeping:
            await interaction.response.send_message("I'm already eeping.")
            return

        self.is_sleeping = True
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity(name="eeping."))

        if duration:
            duration_seconds = duration * 60  # Convert minutes to seconds
            await interaction.response.send_message(f"Eeping for {duration} minutes.")

            async def wake_up():
                await asyncio.sleep(duration_seconds)
                self.is_sleeping = False
                await self.bot.change_presence(status=discord.Status.online)

            if self.wake_up_task:
                self.wake_up_task.cancel()

            self.wake_up_task = asyncio.create_task(wake_up())
        else:
            await interaction.response.send_message("Going to eep")

    @discord.app_commands.command(name="wake", description="Make Blevitron stop ignoring messages.")
    async def wake(self, interaction: discord.Interaction):
        """Make Blevitron stop ignoring messages."""
        if not self.is_sleeping:
            await interaction.response.send_message("I'm awake.")
            return

        self.is_sleeping = False
        await self.bot.change_presence(status=discord.Status.online)
        await interaction.response.send_message("I'm awake now")

        if self.wake_up_task:
            self.wake_up_task.cancel()
            self.wake_up_task = None

async def setup(bot: commands.Bot):
    await bot.add_cog(SleepCog(bot))
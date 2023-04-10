import datetime
import discord
from discord.ext import commands, tasks

RESET_TIME = datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc)

class Tasks(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.habit_reset_timer.start()

    @tasks.loop(seconds=2)
    async def habit_reset_timer(self):
        print('reset habits')

async def setup(client):
    await client.add_cog(Tasks(client))

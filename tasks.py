import datetime

import aiosqlite
import discord
from discord.ext import commands, tasks

RESET_TIME = datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc)
DATABASE = "data/billy.db"

class Tasks(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.habit_reset_timer.start()

    @tasks.loop(time=RESET_TIME)
    async def habit_reset_timer(self):
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(f"""UPDATE user_data SET checklist = NULL;""")
            await db.commit()
        print("It's midnight, i've reset the checklists.")

async def setup(client):
    await client.add_cog(Tasks(client))

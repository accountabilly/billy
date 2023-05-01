#!/bin/python3
import json
import os
import random
import types

import aiosqlite
import discord
from discord.ext import commands

from ext.database import Database

from ext.userfeedback import UserFeedback as uf

# Set to true if running Billy Testing
isTesting = True

PWD = "/home/pim/Nextcloud/Projects/billy/"

# Load API keys and admin data into a pythonic object.
KEYS = json.load(open(PWD+"data/admin.json"), object_hook=lambda d: types.SimpleNamespace(**d))
DATABASE = PWD+"data/billy.db"
COMMIT_HEAD = open(PWD+".git/ORIG_HEAD", 'r').readline()[:7]
database = Database(DATABASE)

intents = discord.Intents.default()
intents.message_content = True

# TODO: Move defaults and settings somewhere else.
HABIT_DEFAULT_MAX = 3
HABIT_CHAR_MAX = 50
PREFIX = '$'

QUOTES = json.load(open(PWD+'texts/quotes.json', encoding='utf-8'))
GREETINGS = json.load(open(PWD+'texts/greetings.json', encoding='utf-8'))['GREETINGS']

class Billy(commands.Bot):
    async def setup_hook(self):
        for filename in os.listdir(PWD):
            if filename.endswith('.py') and not filename == 'main.py':
                await self.load_extension(f'{filename[:-3]}')
                print(f"{filename} loaded successfully.")

client = Billy(command_prefix=PREFIX, intents=intents)

@client.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.watching, name="your progress")
    await client.change_presence(activity=activity)
    if isTesting:
        guild = await client.fetch_guild(841279909326618664)
        billy_member = await guild.fetch_member(client.user.id)
        await billy_member.edit(nick=f"Billy Testing ({COMMIT_HEAD})")
    print(f'We have logged in as {client.user}')


async def send_dm(user_id, message):
    user = await client.fetch_user(user_id)
    await user.send(message)


@client.command()
async def test(ctx):
    user_id = ctx.author.id
    dictionary = await database.fetch_data(user_id)
    print(dictionary)


@client.command()
async def version(ctx):
    if isTesting:
        ver = COMMIT_HEAD
    else:
        ver = KEYS.VERSION
    await ctx.send(f"I'm running version `{ver}`.")


@client.command()
async def quote(ctx):
    quote_choice = random.choice(QUOTES)
    embed = discord.Embed(color=None, title=f""" "{quote_choice['text']}" """,
                          type='rich', description=quote_choice['from'])
    await ctx.send(embed=embed)


@client.command()
async def add_habit(ctx, *, habit=None):

    # Comment
    user_id = ctx.author.id
    data = await database.fetch_data(user_id, 'habits')

    # Error handling
    if habit is None:  # Comment
        await ctx.send(uf.AddHabit.no_habit_error(user_id))

    elif not habit.strip():  # Comment
        await ctx.send(uf.AddHabit.invalid_format_error)

    elif len(data['habits']) >= HABIT_DEFAULT_MAX:
        await ctx.send(uf.AddHabit.max_habit_error(user_id))

    elif len(habit.strip()) > HABIT_CHAR_MAX:
        await ctx.send(uf.AddHabit.max_habit_char_error(user_id))

    elif habit.count("\n") > 0:  # If habit contains any newlines
        await ctx.send(uf.AddHabit.no_newlines_error(user_id))

    else:  # Comment
        async with aiosqlite.connect(DATABASE) as db:

            if data is None:  # Comment
                habits = [habit.lower()]
                await db.execute(f"""INSERT INTO user_data (user_id, habits) VALUES ({user_id}, "{habits}");""")
                await ctx.send(uf.AddHabit.user_created_message(user_id, habit))

            else:  # Comment
                data['habits'].append(habit.lower())
                habit_string = str(data['habits'])
                await db.execute(f"""UPDATE user_data SET habits="{habit_string}" WHERE user_id={user_id};""")
                await ctx.send(uf.AddHabit.habit_added_message(user_id, habit))

            # Comment
            await db.commit()


@client.command()
async def remove_habit(ctx, *, habit_loc=None):

    # Fetch data
    user_id = ctx.author.id
    data = await database.fetch_data(user_id)

    #  Error handling
    if habit_loc is None:  # If user didn't add any input
        await ctx.send(uf.RemoveHabit.no_habit_loc_error(user_id))

    elif data is None:  # If user doesn't have a profile
        await ctx.send(uf.RemoveHabit.no_profile_error(user_id))

    elif len(data['habits']) == 0 or data['habits'] is None:  # If user doesn't have any habits
        await ctx.send(uf.RemoveHabit.no_habits_error(user_id))

    elif not habit_loc.isdigit() or not isinstance(habit_loc, str):  # If habit_loc is not an integer or a string
        await ctx.send(uf.RemoveHabit.incorrect_format_error(user_id))

    # If user input is an integer and is not within range of habits
    elif habit_loc.lstrip('-').isdigit() and not 0 < int(habit_loc) <= len(data['habits']):

        if len(data['habits']) >= 2:  # If user has more than 1 habit
            await ctx.send(uf.RemoveHabit.multi_oor_error(user_id, len(data['habits'])))

        else:  # If user has one habit
            await ctx.send(uf.RemoveHabit.single_oor_error(user_id))

    # If user inout is a string
    elif habit_loc.lower() not in data['habits']:  # If user input is not in habits
        await ctx.send(uf.RemoveHabit.not_found_error(user_id))

    else:  # Errors handled

        # Connect to Billy database
        async with aiosqlite.connect(DATABASE) as db:

            # Index formatting
            if habit_loc.isdigit():  # if user input is integer
                habit_index = int(habit_loc) - 1

            elif isinstance(habit_loc, str):  # if user input is string
                habit_index = data['habits'].index(habit_loc.lower())

            # Remove habit, convert habit to string, update SQL query and execute query
            del data['habits'][habit_index]
            habit_string = str(data['habits'])
            await db.execute(f"""UPDATE user_data SET habits="{habit_string}" WHERE user_id={user_id};""")
            await ctx.send(uf.RemoveHabit.habit_removed_message(user_id, habit_string))
            await db.commit()


@client.command()
async def list_habits(ctx, *, user_input=None):

    # Fetch data
    user_id = ctx.author.id
    data = await database.fetch_data(user_id, 'habits', 'checklist')

    # Error handling
    if data is None:  # If user doesn't have a profile
        await ctx.send(uf.ListHabits.no_profile_error(user_id))

    elif len(data['habits']) == 0 or data['habits'] is None:  # If user doesn't have any habits
        await ctx.send(uf.ListHabits.no_habits_error(user_id))

    elif user_input is not None:
        await ctx.send(uf.ListHabits.input_error(user_id))

    else:  # Errors handled

        checklist = data['checklist']
        # Create an empty list, format each item and join into one formatted string
        habit_list = []

        for i, habit in enumerate(data['habits']):
            string = str(i + 1) + ". " + habit.title()
            if (checklist is not None) and checklist[i] == 1:
                string += " ✅"
            else:
                string += " ❌"

            habit_list.append(string)

        habit_list = "\n".join(habit_list)

        embed = discord.Embed(color=None, title=f"""{ctx.author.display_name}'s habits""",
                              type='rich', description=habit_list)

        await ctx.send(f"{random.choice(GREETINGS)} {ctx.author.mention}", embed=embed)

@client.command()
async def check_habit(ctx, habit):
    try:
        habit = int(habit)
    except:
        pass

    data = await database.fetch_data(ctx.author.id, 'habits', 'checklist')
    habits, checklist = data['habits'], data['checklist']

    print(habits, checklist)

    if checklist is None:
        checklist = [0 for habit in habits]

    print("test")

    if not isinstance(habit, int) or habit > len(habits):
        await ctx.send("Invalid input.")
    else:
        checklist[habit-1] = 1
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(f"""UPDATE user_data SET checklist="{str(checklist)}" WHERE user_id = {ctx.author.id};""")
            await db.commit()

        await ctx.send(f"Habit {habit} checked off successfully.")

client.run(KEYS.DISCORD_SECRET)

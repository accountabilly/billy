#!/bin/python3
import ast
import json
import random
import types

import aiosqlite
import discord
from discord.ext import commands
from github import Github

# Load API keys and admin data into a pythonic object.
KEYS = json.load(open("data/admin.json"), object_hook=lambda d: types.SimpleNamespace(**d))
DATABASE = "data/billy.db"

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='$', intents=intents)

HABIT_DEFAULT_MAX = 3
HABIT_CHAR_MAX = 50

QUOTES = json.load(open('texts/quotes.json', encoding='utf-8'))
GREETINGS = json.load(open('texts/greetings.json', encoding='utf-8'))['GREETINGS']


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

async def send_dm(user_id, message):
    user = await client.fetch_user(user_id)
    await user.send(message)

async def fetch_data(user_id, *columns):

    # Connect to database
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.cursor()

        if columns:  # Get specified columns
            column_names = list(columns)
            query = f"SELECT {','.join(column_names)} FROM user_data WHERE user_id={user_id};"

        else:  # Get all columns
            query = f"SELECT * FROM user_data WHERE user_id={user_id};"
            await cursor.execute(query)
            column_names = [description[0] for description in cursor.description]

        # Execute the query and fetch the data
        await cursor.execute(query)
        row = await cursor.fetchone()

        if row:  # If data was fetched then format data into a database where column name is the key
            data = {}
            for i, value in enumerate(row):

                # Check if the value is a string that looks like a list and parse it
                if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
                    value = ast.literal_eval(value)
                data[column_names[i]] = value

            # Delete 'user_id' key value pair as not required and return data
            if 'user_id' in data:
                del data['user_id']
            return data

        else:  # If no data fetched from database then return None
            return None


@client.command()
async def test(ctx):
    user_id = ctx.author.id
    dictionary = await fetch_data(user_id)
    print(dictionary)


@client.command()
async def hello(ctx):
    await ctx.send("hello")


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
    data = await fetch_data(user_id, 'habits')

    # Error handling messages and message introduction
    salutation = f"{random.choice(GREETINGS)} {ctx.author.mention},\n\n"

    no_habit_error = f"{salutation}"

    invalid_format_error = f"{salutation}"

    max_habit_error = f"{salutation}"

    max_habit_char_error = f"{salutation}"

    no_newlines_error = f"{salutation}"

    user_created_message = f"{salutation}"

    habit_added_message = f"{salutation}"

    # Error handling
    if habit is None:  # Comment
        await ctx.send(no_habit_error)

    elif not habit.strip():  # Comment
        await ctx.send(invalid_format_error)

    elif len(data['habits']) >= HABIT_DEFAULT_MAX:
        await ctx.send(max_habit_error)

    elif len(habit.strip()) > HABIT_CHAR_MAX:
        await ctx.send(max_habit_char_error)

    elif habit.count("\n") > 0:  # If habit contains any newlines
        await ctx.send(no_newlines_error)

    else:  # Comment
        async with aiosqlite.connect(DATABASE) as db:

            if data is None:  # Comment
                habits = [habit.lower()]
                await db.execute(f"""INSERT INTO user_data (user_id, habits) VALUES ({user_id}, "{habits}");""")
                await ctx.send(user_created_message)

            else:  # Comment
                data['habits'].append(habit.lower())
                habit_string = str(data['habits'])
                await db.execute(f"""UPDATE user_data SET habits="{habit_string}" WHERE user_id={user_id};""")
                await ctx.send(habit_added_message)

            # Comment
            await db.commit()


@client.command()
async def remove_habit(ctx, *, habit_loc=None):

    # Fetch data
    user_id = ctx.author.id
    data = await fetch_data(user_id)

    # Error handling messages and message introduction
    salutation = f"{random.choice(GREETINGS)} {ctx.author.mention},\n\n"

    no_habit_loc_error = f"{salutation}"

    no_profile_error = f"{salutation}"

    no_habits_error = f"{salutation}"

    incorrect_format_error = f"{salutation}"

    multi_oor_error = f"{salutation}"

    single_oor_error = f"{salutation}"

    not_found_error = f"{salutation}"

    habit_removed_message = f"{salutation}"

    #  Error handling
    if habit_loc is None:  # If user didn't add any input
        await ctx.send(no_habit_loc_error)

    elif data is None:  # If user doesn't have a profile
        await ctx.send(no_profile_error)

    elif len(data['habits']) == 0 or data['habits'] is None:  # If user doesn't have any habits
        await ctx.send(no_habits_error)

    elif not habit_loc.isdigit() or not isinstance(habit_loc, str):  # If habit_loc is not an integer or a string
        await ctx.send(incorrect_format_error)

    # If user input is an integer and is not within range of habits
    elif habit_loc.lstrip('-').isdigit() and not 0 < int(habit_loc) <= len(data['habits']):

        if len(data['habits']) >= 2:  # If user has more than 1 habit
            await ctx.send(multi_oor_error + f"please choose a number between 1 and {len(data['habits'])}")

        else:  # If user has one habit
            await ctx.send(single_oor_error)

    # If user inout is a string
    elif habit_loc.lower() not in data['habits']:  # If user input is not in habits
        await ctx.send(not_found_error)

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
            await ctx.send(habit_removed_message)
            await db.commit()


@client.command()
async def list_habits(ctx, *, user_input=None):

    # Fetch data
    user_id = ctx.author.id
    data = await fetch_data(user_id, 'habits')

    salutation = f"{random.choice(GREETINGS)} {ctx.author.mention},\n\n"

    no_profile_error = f"{salutation}You don't seem to have a profile with us yet. " \
                       f"To get started, please add a habit using the add habit command e.g.:\n" \
                       f"```$add_habit Wake up at 7am```"

    no_habits_error = f"{salutation}"

    input_error = f""

    # Error handling
    if data is None:  # If user doesn't have a profile
        await ctx.send(no_profile_error)

    elif len(data['habits']) == 0 or data['habits'] is None:  # If user doesn't have any habits
        await ctx.send(no_habits_error)

    elif user_input is not None:
        await ctx.send(input_error)

    else:  # Errors handled

        # Create an empty list, format each item and join into one formatted string
        habit_list = []

        for i, habit in enumerate(data['habits']):
            habit_list.append(str(i + 1) + ". " + habit.title())

        habit_list = "\n".join(habit_list)

        embed = discord.Embed(color=None, title=f"""{ctx.author.display_name}'s habits""",
                              type='rich', description=habit_list)

        await ctx.send(f"{random.choice(GREETINGS)} {ctx.author.mention}", embed=embed)


@client.command(name='create_issue')
async def create_issue(ctx, *, issue_input=None):

    max_title_char_len = 256  # GitHub has a max title char length of 256

    # Error handling messages and message introduction
    salutation = f"{random.choice(GREETINGS)} {ctx.author.mention},\n\n"

    intro = f"Thank you for attempting to notify us of an important bug or potential future enhancement.\n\n" \
            f"Unfortunately your issue had an invalid input format. "

    no_profile_error = f"{salutation + intro[:-54]}You don't seem to have a profile with us yet. " \
                       f"Please add a habit and try using some features first before trying to notify us of any issues."

    no_issue_input_error = f"{intro} No Issue title or Issue Description was entered."

    formatting_error = f"{intro} Please enter the Issue Title and Issue Description " \
                       f"separated by double colons '::' like this:\n" \
                       f"```$create_issue Issue Title::Issue Description```"

    user_id = ctx.author.id
    data = await fetch_data(user_id, 'habits')

    # Error handling
    if data is None:  # If user doesn't have a profile
        await ctx.send(no_profile_error)

    elif issue_input is None:  # If user didn't add any input
        await ctx.send(no_issue_input_error)

    elif issue_input.split("::") != 2:  # If the user didn't format the title and comment correctly
        await ctx.send(formatting_error)

    else:
        # Split into title and comment excess length amount
        title, comment = issue_input.split("::")
        excess_len = len(title) - max_title_char_len

        # Error handling messages
        no_newlines_error = f"{intro} Please do not include newlines in your issue title."

        invalid_title_error = f"{intro} Please provide a valid Issue Title."

        max_char_title_error = f"{intro} Your title was too long by {excess_len} characters. " \
                               f"Please provide a title with a maximum of 256 characters."

        invalid_comment_error = f"{intro} Please provide a valid Issue Description."

        # Error handling
        if title.count("\n") > 0:  # If title contains any newlines
            await ctx.send(no_newlines_error)

        elif not title.strip():  # If title is empty or just whitespace/tabs
            await ctx.send(invalid_title_error)

        elif len(title) >= max_title_char_len:  # If title is more than GitHubs title character maximum
            await ctx.send(max_char_title_error)

        elif not comment.strip():  # If comment is empty or just whitespace/tabs
            await ctx.send(invalid_comment_error)

        else:  # Errors handled

            # Create issue on GitHub
            g = Github(KEYS.GIT.TOKEN)
            repo = g.get_repo(f"{KEYS.GIT.USER}/{KEYS.GIT.REPO}")
            issue = repo.create_issue(title=title, body=comment)

            # Issue created confirmation messages
            user_confirmation_message = f"{random.choice(GREETINGS)} {ctx.author.mention},\n\n" \
                                        f"Issue #{issue.number} created ✅\n" \
                                        f"```Issue title:\n{title}\n" \
                                        f"Issue body:\n{comment}\n```" \
                                        f"You can keep up to date with the progress of this issue here:\n" \
                                        f"{issue.html_url}"

            admin_confirmation_message = f"Issue raised ✅\n" \
                                         f"Name: {ctx.author.name}\n" \
                                         f"User ID: {ctx.author}\n" \
                                         f"From: {ctx.guild}"

            # Send issue confirmation message to the channel
            await ctx.send(user_confirmation_message)

            # Send issue confirmation message to Billy Bot admins
            for i in ADMINS:
                await send_dm(i, admin_confirmation_message)


client.run(KEYS.DISCORD_SECRET)

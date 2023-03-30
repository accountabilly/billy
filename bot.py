#!/bin/python3
import discord
from discord.ext import commands
import json
import random
import aiosqlite
import ast
from github import Github

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='$', intents=intents)

# TODO: move sensitive data to .gitignore file
DISCORD_TOKEN = 'MTA2NDYzNDI5MTA3OTg4MDc1NA.Ga9c92.VP3Y1bY8PUZkKFv4RCAgfRRfeCU1byWAy9GStc'
DATABASE = "data/billy.db"
GIT_USER = "pim-wtf"
GIT_REPO = "billy"
GIT_TOKEN = "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"
ADMINS = [142368509664428032, 445248853613084672]
GREETINGS = ["Hello", "Hi", "Hey", "Howdy", "Bonjour", "Salut", "Hola", "Buenos días", "Guten Tag", "Kon'nichiwa",
             "Salam", "Shalom", "Namaste", "Sawasdee", "Ni hao", "Annyeonghaseyo", "Zdravstvuyte", "Aloha", "Ahoy",
             "Hej", "Ciao"]
HABIT_DEFAULT_MAX = 3
HABIT_CHAR_MAX = 50
quotes = []


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    global quotes
    quotes = json.load(open('data/quotes.json', encoding='utf-8'))


async def send_dm(user_id, message):
    user = await client.fetch_user(user_id)
    await user.send(message)


async def fetch_data(user_id, *columns):
    """

    :param user_id:
    :param columns:
    :return:
    """

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
    quote_choice = random.choice(quotes)
    embed = discord.Embed(color=None,
                          title=f""" "{quote_choice['text']}" """,
                          type='rich',
                          description=quote_choice['from'])
    await ctx.send(embed=embed)


@client.command()
async def add_habit(ctx, *, habit=None):
    # Comment
    user_id = ctx.author.id
    data = await fetch_data(user_id, 'habits')
    intro = f"{random.choice(GREETINGS)} {ctx.author.mention},\n\n"

    if habit is None:  # Comment
        await ctx.send(f"No habit specified")

    elif not habit.strip():  # Comment
        await ctx.send(f"Habit has an incorrect format")

    elif len(data['habits']) >= HABIT_DEFAULT_MAX:
        print(data['habits'])
        print(len(data['habits']))
        await ctx.send(f"Maximum habits reached")

    elif len(habit.strip()) > HABIT_CHAR_MAX:
        # TODO: Maximum character length message
        await ctx.send(f"Maximum character length exceeded")

    else:  # Comment
        async with aiosqlite.connect(DATABASE) as db:

            if data is None:  # Comment
                habits = [habit.lower()]
                await db.execute(f"""INSERT INTO user_data (user_id, habits) VALUES ({user_id}, "{habits}");""")
                await ctx.send(f"Profile created and added your first habit")

            else:  # Comment
                data['habits'].append(habit.lower())
                habit_string = str(data['habits'])
                await db.execute(f"""UPDATE user_data SET habits="{habit_string}" WHERE user_id={user_id};""")
                # TODO: add habit message
                await ctx.send(f"Habit added")

            # Comment
            await db.commit()


@client.command()
async def remove_habit(ctx, *, habit_loc=None):
    """

    :param ctx:
    :param habit_loc:
    :return:
    """

    # Comment
    user_id = ctx.author.id
    data = await fetch_data(user_id)

    # Comment
    if habit_loc is None:
        await ctx.send(f'habit to delete unspecified')

    # Comment
    elif data is None:
        await ctx.send(f'No profile exits')

    # Comment
    elif len(data['habits']) == 0 or data['habits'] is None:
        await ctx.send(f'you dont have any habits')

    # Comment
    elif not habit_loc.isdigit() and not isinstance(habit_loc, str):
        await ctx.send(f"incorrect format")

    # Comment
    elif habit_loc.lstrip('-').isdigit() and not 0 < int(habit_loc) <= len(data['habits']):
        await ctx.send(f'I am hitting this')

        # Comment
        if (int(habit_loc) <= 0 or int(habit_loc) > len(data['habits'])) and len(data['habits']) >= 2:
            await ctx.send(f"please choose a number between 1 and {len(data['habits'])}")

        else:  # Comment
            await ctx.send(f"you only have one habit")

    # Comment
    elif isinstance(habit_loc, str) and habit_loc.lower() not in data['habits'] and not habit_loc.isdigit():
        await ctx.send(f'habit cannot be found')

    else:  # Comment

        # Comment
        async with aiosqlite.connect(DATABASE) as db:

            # Comment
            if habit_loc.isdigit():
                habit_index = int(habit_loc) - 1

            # Comment
            elif isinstance(habit_loc, str):
                habit_index = data['habits'].index(habit_loc.lower())

            else:  # Comment
                print(f"unknown error")

            # Comment
            del data['habits'][habit_index]
            habit_string = str(data['habits'])
            await db.execute(f"""UPDATE user_data SET habits="{habit_string}" WHERE user_id={user_id};""")
            await ctx.send(f'habit removed')
            await db.commit()


@client.command()
async def list_habits(ctx):
    # TODO: Comments
    # Fetch data
    user_id = ctx.author.id
    data = await fetch_data(user_id, 'habits')

    if data is None:  # Comment
        await ctx.send("No profile exists")

    # Comment
    elif len(data['habits']) == 0 or data['habits'] is None:
        # TODO: you have no habits message
        await ctx.send("You have no habits")

    else:  # Comment
        habit_list = []

        for i, habit in enumerate(data['habits']):
            habit_list.append(str(i + 1) + ". " + habit.title())

        habit_list = "\n".join(habit_list)

        embed = discord.Embed(color=None,
                              title=f"""{ctx.author.display_name}'s habits""",
                              type='rich',
                              description=habit_list)

        await ctx.send(f"{random.choice(GREETINGS)} {ctx.author.mention}", embed=embed)


@client.command(name='create_issue')
async def create_issue(ctx, *, issue_input=None):

    # Formatting the issue and error handling
    intro = f"{random.choice(GREETINGS)} {ctx.author.mention},\n\n" \
            f"Thank you for attempting to notify us of a bug or potential future enhancement.\n\n" \
            f"Unfortunately your issue had an invalid input format."
    if issue_input is not None:
        issue_parts = issue_input.split("::")
        if len(issue_parts) != 2:
            await ctx.send(f"{intro} Please enter the Issue Title and Issue Description "
                           f"separated by double colons '::' like this:\n"
                           f"```$create_issue Issue Title::Issue Description```")
        else:
            title, comment = issue_parts
            if not title.strip():
                await ctx.send(f"{intro} Please provide a valid Issue Title.")
            elif len(title) >= 256:
                excess_len = len(title) - 256
                await ctx.send(f"{intro} Your title was too long by {excess_len} characters. "
                               f"Please provide a title with a maximum of 256 characters.")
            elif not comment.strip():
                await ctx.send(f"{intro} Please provide a valid Issue Description.")
            else:
                # Create issue on GitHub

                g = Github(GIT_TOKEN)
                repo = g.get_repo(f"{GIT_USER}/{GIT_REPO}")
                issue = repo.create_issue(title=title, body=comment)

                # Send issue confirmation message to the channel

                await ctx.send(f"Issue #{issue.number} created ✅\n"
                               f"```Issue title:\n{title}\n"
                               f"Issue body:\n{comment}\n```"
                               f"You can keep up to date with the progress of this issue here:\n{issue.html_url}")

                # Send bot admins a message

                message = f"Issue raised ✅\n" \
                          f"Name: {ctx.author.name}\n" \
                          f"User ID: {ctx.author}\n" \
                          f"From: {ctx.guild}"
                for i in ADMINS:
                    await send_dm(i, message)
    else:
        await ctx.send(f"{intro} No Issue title or Issue Description was entered.")


client.run(DISCORD_TOKEN)

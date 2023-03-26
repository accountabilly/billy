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

    # Git info:
GIT_USER = "pim-wtf"
GIT_REPO = "billy"
GIT_TOKEN = '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'
ADMINS = [142368509664428032, 445248853613084672]

client = commands.Bot(command_prefix='$', intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    global quotes
    quotes = json.load(open('data/quotes.json', encoding='utf-8'))

async def send_dm(user_id, message):
    user = await client.fetch_user(user_id)
    await user.send(message)

@client.command()
async def hello(ctx):
    await ctx.send("hello")

@client.command()
async def quote(ctx):
    choice = random.choice(quotes)
    embed = discord.Embed(color=None,
                  title=f""" "{choice['text']}" """,
                  type='rich',
                  description=choice['from'])
    await ctx.send(embed=embed)

@client.command()
async def add_habit(ctx, *, habit):
    user_id = ctx.author.id

    async with aiosqlite.connect("data/billy.db") as db:
        cursor = await db.execute(f"SELECT * FROM user_data WHERE user_id={user_id};")
        result = await cursor.fetchall()
        print(result)

        if not len(result) == 0:
            habits = ast.literal_eval(result[0][1])
            habits.append(habit)
            h = str(habits)
            await db.execute(f"""UPDATE user_data SET habits="{h}" WHERE user_id={user_id};""")
        else:
            habits = [habit]
            await db.execute(f"""INSERT INTO user_data (user_id, habits) VALUES ({user_id}, "{habits}");""")

        await db.commit()

@client.command()
async def list_habits(ctx):
    user_id = ctx.author.id

    async with aiosqlite.connect("data/billy.db") as db:
        cursor = await db.execute(f"SELECT habits FROM user_data WHERE user_id={user_id};")
        result = await cursor.fetchall()
        habit_list = []

        for i, habit in enumerate(ast.literal_eval(result[0][0])):
            habit_list.append(str(i+1) + ". " + habit)

        habit_list = "\n".join(habit_list)

        embed = discord.Embed(color=None,
                              title=f"""{ctx.author.display_name}'s habits""",
                              type='rich',
                              description=habit_list)

        await ctx.send(ctx.author.mention, embed=embed)


@client.command(name= 'create_issue')
async def create_issue(ctx, *, issue_input):

    title, comment = issue_input.split("::")

    await ctx.send(title)
    await ctx.send(comment)

    g = Github(GIT_TOKEN)
    repo = g.get_repo(f"{GIT_USER}/{GIT_REPO}")
    issue = repo.create_issue(title=title, body=comment)
    await ctx.send(f"Issue {issue.number} created: {issue.html_url}")
        # Send bot admins a message
    message = f"\n\n Issue raised by\n{ctx.author.name}\n{ctx.author.id}\nfrom {ctx.guild}"
    for i in ADMINS:
        await send_dm(i, message)

client.run('MTA2NDYzNDI5MTA3OTg4MDc1NA.Ga9c92.VP3Y1bY8PUZkKFv4RCAgfRRfeCU1byWAy9GStc')

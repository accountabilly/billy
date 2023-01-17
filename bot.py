#!/bin/python3
import discord
from discord.ext import commands
import json
import random


intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='$', intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    global quotes
    quotes = json.load(open('quotes.json', encoding='utf-8'))


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

client.run('MTA2NDYzNDI5MTA3OTg4MDc1NA.Ga9c92.VP3Y1bY8PUZkKFv4RCAgfRRfeCU1byWAy9GStc')

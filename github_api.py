import json
import random
import types

import discord
from discord.ext import commands, tasks
from github import Github

from ext.database import Database
from ext.userfeedback import UserFeedback as uf

# Load API keys and admin data into a pythonic object.
PWD = "/home/pim/Nextcloud/Projects/billy/"
KEYS = json.load(open(PWD+"data/admin.json"), object_hook=lambda d: types.SimpleNamespace(**d))
GREETINGS = json.load(open(PWD+'texts/greetings.json', encoding='utf-8'))['GREETINGS']

db = Database(PWD+"data/billy.db")

class GithubAccess(commands.Cog, name="Github"):
    def __init__(self, client):
        self.client = client

    async def send_dm(self, user_id, message):
        user = await self.client.fetch_user(user_id)
        await user.send(message)

    @commands.command()
    async def create_issue(self, ctx, *, issue_input=None):

        max_title_char_len = 256  # GitHub has a max title char length of 256
        data = await db.fetch_data(ctx.author.id, 'habits')

        # Error handling
        if data is None:  # If user doesn't have a profile
            await ctx.send(uf.CreateIssue.no_profile_error(ctx.author))

        elif issue_input is None:  # If user didn't add any input
            await ctx.send(uf.CreateIssue.no_issue_input_error(ctx.author))

        elif len(issue_input.split("::")) != 2:  # If the user didn't format the title and comment correctly
            await ctx.send(uf.CreateIssue.formatting_error(ctx.author))

        else:
            # Split into title and comment excess length amount
            title, comment = issue_input.split("::")
            excess_len = len(title) - max_title_char_len

            bot_footer = f"\n\nThis issue was automatically raised by `{ctx.author}` via Discord."

            # Error handling
            if title.count("\n") > 0:  # If title contains any newlines
                await ctx.send(uf.CreateIssue.no_newlines_error)

            elif not title.strip():  # If title is empty or just whitespace/tabs
                await ctx.send(uf.CreateIssue.invalid_title_error)

            elif len(title) >= max_title_char_len:  # If title is more than GitHubs title character maximum
                await ctx.send(uf.CreateIssue.max_char_title_error)

            elif not comment.strip():  # If comment is empty or just whitespace/tabs
                await ctx.send(uf.CreateIssue.invalid_comment_error)

            else:  # Errors handled

                # Create issue on GitHub
                g = Github(KEYS.GIT.TOKEN)
                repo = g.get_repo(f"{KEYS.GIT.USER}/{KEYS.GIT.REPO}")
                issue = repo.create_issue(title=title, body=comment+bot_footer)

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
                for i in KEYS.ADMINS:
                    await self.send_dm(i, admin_confirmation_message)

async def setup(client):
    await client.add_cog(GithubAccess(client))

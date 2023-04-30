import json
import random
import types

import discord
from discord.ext import commands, tasks
from github import Github

from ext.database import Database

# Load API keys and admin data into a pythonic object.
PWD = "/home/pi/billy/"
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

        data = await db.fetch_data(ctx.author.id, 'habits')

        # Error handling
        if data is None:  # If user doesn't have a profile
            await ctx.send(no_profile_error)

        elif issue_input is None:  # If user didn't add any input
            await ctx.send(no_issue_input_error)

        elif len(issue_input.split("::")) != 2:  # If the user didn't format the title and comment correctly
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

            bot_footer = f"\n\nThis issue was automatically raised by `{ctx.author}` via Discord."

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

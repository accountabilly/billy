import random


class UserFeedback:

    GREETINGS = ["Hello", "Hi", "Hey", "Howdy", "Bonjour", "Salut", "Hola", "Buenos días", "Guten Tag", "Kon'nichiwa",
                 "Salam", "Shalom", "Namaste", "Sawasdee", "Ni hao", "Annyeonghaseyo", "Zdravstvuyte", "Aloha", "Ahoy",
                 "Hej", "Ciao"]

    HABIT_EXAMPLES = ["Wake up at 7am", "Running", "Read", "Study", "Piano practise", "Guitar practise",
                      "Language study", "Workout", "Yoga"]

    @staticmethod
    def salutation(user):
        return f"{random.choice(UserFeedback.GREETINGS)} {user.mention},\n\n"

    class AddHabit:
        @staticmethod
        def no_habit_error(user):
            return f"{UserFeedback.salutation(user)}No habit provided. " \
                   f"Please make sure to give your habit a name e.g.:\n" \
                   f"```$add_habit {random.choice(UserFeedback.HABIT_EXAMPLES)}```"

        @staticmethod
        def invalid_format_error(user):
            return f"{UserFeedback.salutation(user)}Your habit has not been formatted correctly. Please try again."

        @staticmethod
        def max_habit_error(user):
            return f"{UserFeedback.salutation(user)}You have already reached your maximum amount of habits."

        @staticmethod
        def max_habit_char_error(user):
            return f"{UserFeedback.salutation(user)}Your habit name is too long. Please choose a smaller, " \
                   f"more concise name."

        @staticmethod
        def no_newlines_error(user):
            return f"{UserFeedback.salutation(user)}Please create a habit without a newline."

        @staticmethod
        def habit_added_message(user, habit, salutation=True):
            message = f"Your habit '{habit}' has been added."
            if salutation:
                return f"{UserFeedback.salutation(user)}{message}"
            else:
                return f"\n\n{message}"

        @staticmethod
        def user_created_message(user, habit):
            return f"{UserFeedback.salutation(user)}Congratulations! Your first habit has been added and your " \
                   f"Account-a-billy profile has been created. Well done for making this first step to creating " \
                   f"a positive, long lasting habit." \
                + UserFeedback.AddHabit.habit_added_message(user, habit, salutation=False)

    class RemoveHabit:
        @staticmethod
        def no_habit_loc_error(user):
            return f"{UserFeedback.salutation(user)}You haven't specified which habit to delete"

        @staticmethod
        def no_profile_error(user):
            return f"{UserFeedback.salutation(user)}You haven't got a profile with us. Please try adding a habit" \
                   f" which will automatically create a profile with us. "

        @staticmethod
        def no_habits_error(user):
            return f"{UserFeedback.salutation(user)}You haven't got any habits at the moment. Please add a habit"

        @staticmethod
        def incorrect_format_error(user):
            return f"{UserFeedback.salutation(user)}Please use the correct format and try again."

        @staticmethod
        def multi_oor_error(user, habit_amount):
            return f"{UserFeedback.salutation(user)}You only have {habit_amount} habits."

        @staticmethod
        def single_oor_error(user):
            return f"{UserFeedback.salutation(user)}You only have 1 habit."

        @staticmethod
        def not_found_error(user):
            return f"{UserFeedback.salutation(user)}I can't find that habit. Please check the spelling and try again." \
                   f" Alternatively, use the corresponding number as the habit locator."

        @staticmethod
        def habit_removed_message(user, habit):
            return f"{UserFeedback.salutation(user)}Your habit '{habit} was removed."

    class ListHabits:

        @staticmethod
        def no_profile_error(user):
            return f"{UserFeedback.salutation(user)}You don't seem to have a profile with us yet. " \
                           f"To get started, please add a habit using the add habit command e.g.:\n" \
                           f"```$add_habit {random.choice(UserFeedback.HABIT_EXAMPLES)}``"

        @staticmethod
        def no_habits_error(user):
            return f"{UserFeedback.salutation(user)}You haven't got any habits at the moment. " \
                   f"Please add a habit using the add habit command e.g.:\n" \
                   f"```$add_habit {random.choice(UserFeedback.HABIT_EXAMPLES)}```"

        @staticmethod
        def input_error(user):
            return f"{UserFeedback.salutation(user)}"

    # TODO: CheckHabit

    class CreateIssue:

        @staticmethod
        def intro(user):
            return f"{UserFeedback.salutation(user)}Thank you for attempting to notify us of an important bug" \
                   f" or potential future enhancement.\n\n" \
                   f"Unfortunately your issue had an invalid input format. "

        @staticmethod
        def no_profile_error(user):
            return f"{UserFeedback.CreateIssue.intro(user)[:-54]}" \
                   f"You don't seem to have a profile with us yet. " \
                   f"Please add a habit and try using some features first before trying to notify us of any issues."

        @staticmethod
        def no_issue_input_error(user):
            return f"{UserFeedback.CreateIssue.intro(user)} No Issue title or Issue Description was entered."

        @staticmethod
        def formatting_error(user):
            return f"{UserFeedback.CreateIssue.intro(user)} Please enter the Issue Title and Issue Description " \
                   f"separated by double colons '::' like this:\n" \
                   f"```$create_issue Issue Title::Issue Description```"

        @staticmethod
        def no_newlines_error(user):
            return f"{UserFeedback.CreateIssue.intro(user)} Please do not include newlines in your issue title."

        @staticmethod
        def invalid_title_error(user):
            return f"{UserFeedback.CreateIssue.intro(user)} Please provide a valid Issue Title."

        @staticmethod
        def max_char_title_error(user, excess_len):
            return f"{UserFeedback.CreateIssue.intro(user)} Your title was too long by {excess_len} characters. " \
                   f"Please provide a title with a maximum of 256 characters."

        @staticmethod
        def invalid_comment_error(user):
            return f"{UserFeedback.CreateIssue.intro(user)} Please provide a valid Issue Description."

        @staticmethod
        def user_confirmation_message(user, issue, comment, title):
            return f"{UserFeedback.salutation(user)}Issue #{issue.number} created ✅\n" \
                   f"```Issue title:\n{title}\n" \
                   f"Issue body:\n{comment}\n```" \
                   f"You can keep up to date with the progress of this issue here:\n" \
                   f"{issue.html_url}"

        @staticmethod
        def admin_confirmation_message(ctx):
            return f"Issue raised ✅\n" \
                   f"Name: {ctx.author.name}\n" \
                   f"User ID: {ctx.author}\n" \
                   f"From: {ctx.guild}"

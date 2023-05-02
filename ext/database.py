import ast
import aiosqlite


class Database:
    def __init__(self, path):
        self.path = path

    async def fetch_data(self, user_id, *columns):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.cursor()
            if columns:  # Get specified columns
                column_names = list(columns)
                query = f"SELECT {','.join(column_names)} FROM user_data WHERE user_id={user_id}"
            else:  # Get all columns
                query = f"SELECT * FROM user_data WHERE user_id={user_id};"

            await cursor.execute(query)
            column_names = [description[0] for description in cursor.description]
            row = await cursor.fetchone()

            if row:  # If data was fetched then format data into a database where column name i
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
            else:
                return None

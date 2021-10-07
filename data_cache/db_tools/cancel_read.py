import pandas as pd
import psycopg2

# Import .env variables #
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
DATABASE_URL = os.getenv('DATABASE_URL')

# create a new database connection by calling the connect() function
con = psycopg2.connect(DATABASE_URL)

#  create a new cursor
cur = con.cursor()

# query
query = f"""SELECT *
            FROM cancel_db
            """

# return results as a dataframe
results = pd.read_sql(query, con)

print(results.head())

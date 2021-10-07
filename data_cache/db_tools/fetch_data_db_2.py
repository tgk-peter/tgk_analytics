import pandas as pd
import psycopg2

# Import .env variables #
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
DATABASE_URL = os.getenv('DATABASE_URL')


con = psycopg2.connect(DATABASE_URL)
cur = con.cursor()
query = f"""SELECT *
            FROM cancel_db
            """
df_cancel = pd.read_sql(query, con)
con.close()

print(df_cancel.columns)

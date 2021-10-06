# import the relevant sql library
from sqlalchemy import create_engine
import pandas as pd

# Import .env variables #
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
DATABASE_URL = os.getenv('DATABASE_URL')

# Example dataframe
data = {'Name': ['Tom', 'nick', 'krish', 'jack'],
        'Age': [20, 21, 19, 18]}
df = pd.DataFrame(data)


# link to your database
engine = create_engine(DATABASE_URL, echo=False)
# attach the data frame (df) to the database with a name of the
# table; the name can be whatever you like
df.to_sql('test_db', con=engine, if_exists='append')

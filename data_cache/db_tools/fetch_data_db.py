# import the relevant sql library
from sqlalchemy import create_engine

# Import .env variables #
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
DATABASE_URL = os.getenv('DATABASE_URL')


# link to your database
engine = create_engine(DATABASE_URL, echo=False)

# run a quick test
print(engine.execute('SELECT * FROM cancel_db').fetchone())

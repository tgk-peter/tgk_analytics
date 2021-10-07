# import the relevant sql library
from sqlalchemy import MetaData
from sqlalchemy import create_engine
# from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

# Import .env variables #
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
DATABASE_URL = os.getenv('DATABASE_URL')


# delete table
engine = create_engine(DATABASE_URL, echo=False)

def drop_table(table_name, engine=engine):
    Base = declarative_base()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    table = metadata.tables[table_name]
    if table is not None:
        Base.metadata.drop_all(engine, [table], checkfirst=True)


drop_table('test_db')

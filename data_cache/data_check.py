### Import Packages ###
import requests
import json
import time
import pandas as pd
import cryptpandas as crp

### Import .env variables
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
CRP_PASSWORD = os.getenv('CRP_PASSWORD')

# Decrypt dataframe
df_cancel = crp.read_encrypted(path='cancel_sub_cache.crypt', password=CRP_PASSWORD)
print(df_cancel.info())
print(df_cancel['cancellation_reason'].value_counts())

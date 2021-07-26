# data_fetch.py = fetch and store data from APIs

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
RECHARGE_API_TOKEN = os.getenv('RECHARGE_API_TOKEN')
CRP_PASSWORD = os.getenv('CRP_PASSWORD')

### Access and Store Cancelled Subscriptions from Recharge ###
# Set request variables
headers = {'X-Recharge-Access-Token': RECHARGE_API_TOKEN}
status = 'CANCELLED'
limit = 250

# Access and store first page of results

# Keep results short for testing. Uncomment when done.

url = f'https://api.rechargeapps.com/subscriptions?status={status}&limit={limit}'

result = requests.get(url, headers=headers)
result_data = result.json()
total_results = result_data['subscriptions']

# While Next Link is present, access and store next page
while 'next' in result.links:
  next_url = result.links['next']['url']
  result = requests.get(next_url, headers=headers)
  result_data = result.json()
  total_results.extend(result_data['subscriptions'])
  # Sleep to avoid rate limit if approach threshold
  if result.headers['X-Recharge-Limit'] == '39/40':
    time.sleep(0.5)

### Create, encrypt, store dataFrames ###

## Create df from json results
df = pd.json_normalize(total_results)

## Slice a new dataframe that keeps customer email, when they cancelled,
## the primary reason they cancelled, and the cancellation comments they left.
columns = ['email', 'cancelled_at', 'cancellation_reason',
            'cancellation_reason_comments']
df_cancel = df.loc[:, columns]
# Convert 'cancelled_at' values to datetime format.
df_cancel['cancelled_at'] = pd.to_datetime(df_cancel['cancelled_at'])
# Replace null in 'cancellation_reason' with 'None'
df_cancel['cancellation_reason'].fillna('None', inplace=True)

## Encrypt and store the df
#encrypt_dir = '/content/drive/MyDrive/Colab Notebooks/analytics_dash/data'
crp.to_encrypted(df_cancel, password=CRP_PASSWORD, path='cancel_sub_cache.crypt')

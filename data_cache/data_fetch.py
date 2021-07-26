# data_fetch.py = fetch and store data from APIs

### Import Packages ###
import requests
import json
import time
import pandas as pd

### Import .env variables
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
RECHARGE_API_TOKEN = os.getenv('RECHARGE_API_TOKEN')

### Access and Store Cancelled Subscriptions from Recharge ###
# Set request variables
headers = {"X-Recharge-Access-Token": RECHARGE_API_TOKEN}
status = "CANCELLED"
limit = 250

# Access and store first page of results

# Keep results short for testing. Uncomment when done.
#url = f"https://api.rechargeapps.com/subscriptions?status={status}&limit={limit}"
url = f"https://api.rechargeapps.com/subscriptions?status={status}&limit={limit}&created_at_min=2021-06-01"

result = requests.get(url, headers=headers)
result_data = result.json()
total_results = result_data['subscriptions']

# While Next Link is present, access and store next page
while "next" in result.links:
  next_url = result.links["next"]["url"]
  result = requests.get(next_url, headers=headers)
  result_data = result.json()
  total_results.extend(result_data['subscriptions'])
  # Sleep to avoid rate limit if approach threshold
  if result.headers['X-Recharge-Limit'] == '39/40':
    time.sleep(0.5)

### Create DataFrames ###

## All data
df = pd.json_normalize(total_results)
print(df.head())

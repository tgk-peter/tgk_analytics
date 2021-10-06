# cancel_store.py
# Fetch data from Recharge API and store in database
# to reduce execution time in Dash app.

###########
# IMPORTS #
###########

# Import Packages #
import cryptpandas as crp
from github import Github
import json
import pandas as pd
import requests
import time


# Import .env variables #
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
RECHARGE_API_TOKEN = os.getenv('RECHARGE_API_TOKEN')
CRP_PASSWORD = os.getenv('CRP_PASSWORD')
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')

###############################################
### Get Data from Recharge Subscription API ###
###############################################

def get_recharge_sub_api(status):
    '''Request and hold paginated data from the Recharge Subscription API

    Keyword arguments:
    status -- that status of the subscription ('ACTIVE', 'CANCELLED', 'EXPIRED')
    '''
    # Set request variables
    headers = {'X-Recharge-Access-Token': RECHARGE_API_TOKEN}
    status = status
    limit = 250

    # Access and store first page of subscription results
    url = f'https://api.rechargeapps.com/subscriptions?\
    status={status}&limit={limit}'
    response = requests.get(url, headers=headers)
    response_data = response.json()
    all_records = response_data['subscriptions']

    # While Next Link is present, access and store next page
    while 'next' in response.links:
      next_url = response.links['next']['url']
      response = requests.get(next_url, headers=headers)
      response_data = response.json()
      all_records.extend(response_data['subscriptions'])
      # Sleep to avoid rate limit if approach threshold
      if response.headers['X-Recharge-Limit'] == '39/40':
        time.sleep(0.5)

    return all_records

def generate_dataframe(records, path):
    '''Create, encrypt, store cancellation DataFrame

    Keyword arguments:
    records -- dictionary of records from API
    path -- file path to write encrypted DataFrame
    '''
    ## Create df from json results
    df = pd.json_normalize(records)

    # Keep columns customer email, when they cancelled,
    # the primary reason they cancelled, cancellation comments left.
    # RESOLVE: encryption fails on full dataframe
    columns = ['email', 'cancelled_at', 'cancellation_reason',
                'cancellation_reason_comments']
    df_cancel = df.loc[:, columns]
    # Convert 'cancelled_at' values to datetime format.
    df_cancel['cancelled_at'] = pd.to_datetime(df_cancel['cancelled_at'])
    # Replace null in 'cancellation_reason' with 'None'
    df_cancel['cancellation_reason'].fillna('None', inplace=True)

    # Encrypt and store the df locally
    crp.to_encrypted(df_cancel, password=CRP_PASSWORD, \
    path=path)

def github_update(file_path):
    '''Read file content and update in github repository

    Keyword arguments:
    file_path -- path of file to read and update
    '''
    with open(file_path) as file:
        file_content = file.read()
    github = Github(GITHUB_ACCESS_TOKEN)
    repo = github.get_user().get_repo("tgk_analytics")
    contents = repo.get_contents(file_path)
    repo.update_file(
        path=contents.path,
        message='next commit',
        content=file_content,
        sha=contents.sha,
    )

### Get all cancelled subscriptions ###
cancellation_records = get_recharge_sub_api(
    status = 'CANCELLED',
)
generate_dataframe(
    records = cancellation_records,
    path = 'data_cache/cancel_sub_cache.crypt',
)
github_update(
    file_path = 'data_cache/cancel_sub_cache.crypt',
)

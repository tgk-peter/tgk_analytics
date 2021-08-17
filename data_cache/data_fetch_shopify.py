# data_fetch.py
# Cache data from Recharge API to reduce execution time in Dash app.

###############
### IMPORTS ###
###############

### Import Packages ###
import requests
import json
import time
import pandas as pd
import cryptpandas as crp
from github import Github

### Import .env variables ###
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
RECHARGE_API_TOKEN = os.getenv('RECHARGE_API_TOKEN')
CRP_PASSWORD = os.getenv('CRP_PASSWORD')
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')

###############################################
### Get Data from Shopify Order API ###
###############################################
def get_shopify_order_api(endpoint, status):
    '''Request and hold paginated data from the Shopify Order API

    Keyword arguments:
    status -- that status of the order('open', 'closed', 'cancelled', 'any')
    endpoint -- the target Shopify endpoint

    Reference:
    https://shopify.dev/api/admin/rest/reference/orders/order
    '''
    # Set URL variables
    headers = {"X-Shopify-Access-Token":SHOPIFY_PASSWORD, \
    "Content-Type":"application/json"}
    shop = "the-good-kitchen-esc.myshopify.com"
    endpoint = endpoint
    status = status
    limit = 250

    # Access and store first page of results
    url = f"https://{shop}/{endpoint}?status={status}&limit={limit}"
    response = requests.get(url, headers=headers)
    response_data = response.json()
    all_records = response_data['orders']

    # While Next Link is present, access and store next page
    while "next" in response.links:
      next_url = response.links["next"]["url"]
      response = requests.get(next_url, headers=headers)
      response_data = response.json()
      all_records.extend(response_data['orders'])
      # Sleep to avoid rate limit if approach bucket size
      if response.headers['X-Shopify-Shop-Api-Call-Limit'] == '79/80':
        time.sleep(0.25)
    return all_records

#########

def generate_cancellation_df(records, path):
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
    status='CANCELLED',
)
generate_cancellation_df(
    records=cancellation_records,
    path='data_cache/cancel_sub_cache.crypt',
)
github_update(
    file_path='data_cache/cancel_sub_cache.crypt',
)

### Get all active Shopify orders ###
active_orders = get_shopify_order_api(
    endpoint= 'admin/api/2021-07/orders.json',
    status='any',
)

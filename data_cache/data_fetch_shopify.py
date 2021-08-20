# data_fetch_shopify.py
# Cache data from Shopify API to reduce execution time in Dash app.

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
CRP_PASSWORD = os.getenv('CRP_PASSWORD')
SHOPIFY_PASSWORD = os.getenv('SHOPIFY_PASSWORD')

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
    # Set URL
    headers = {"X-Shopify-Access-Token":SHOPIFY_PASSWORD, \
    "Content-Type":"application/json"}
    shop = "the-good-kitchen-esc.myshopify.com"
    endpoint = endpoint
    status = status
    limit = 250
    created_at_min = "2021-04-10T14:31:59-04:00"
    created_at_max = "2021-05-10T14:31:59-04:00"
    fields = 'email,order_number,created_at,cancelled_at,line_items'
    url = f"https://{shop}/{endpoint}?fields={fields}&status={status}&limit={limit}&created_at_min={created_at_min}"

    # Access and store first page of results
    session = requests.Session()
    response = session.get(url, headers=headers)
    response_data = response.json()
    all_records = response_data['orders']

    # While Next Link is present, access and store next page
    while "next" in response.links:
      next_url = response.links["next"]["url"]
      response = session.get(next_url, headers=headers)
      response_data = response.json()
      all_records.extend(response_data['orders'])
      # Sleep to avoid rate limit if approach bucket size
      if response.headers['X-Shopify-Shop-Api-Call-Limit'] == '79/80':
        time.sleep(0.25)
    return all_records

#########

def generate_active_order_df(records, path):
    '''Create, encrypt, store cancellation DataFrame

    Keyword arguments:
    records -- dictionary of records from API
    path -- file path to write encrypted DataFrame
    '''

    # Generate df from json and trim it to target
    # Keep active (non-cancelled) subscription orders.
    # Keep customer email, order number, order creation date,
    # subscription sku, and cancelled_at date.
    # Convert created_at to datetime
    df_orders_sub = pd.json_normalize(records, record_path='line_items', \
                            meta=['email', 'order_number', 'created_at', 'cancelled_at'])
    df_orders_sub = df_orders_sub.loc[:, ['email', 'order_number', 'created_at', 'sku', 'cancelled_at']]
    df_orders_sub['created_at'] = pd.to_datetime(df_orders_sub['created_at'])
    df_orders_sub = df_orders_sub[df_orders_sub['sku'].str.contains('SUB')]
    df_orders_sub = df_orders_sub[df_orders_sub['cancelled_at'].isnull()]

    # Encrypt and store the df locally
    crp.to_encrypted(df_orders_sub, password=CRP_PASSWORD, \
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

### Get all active Shopify orders ###
active_orders = get_shopify_order_api(
    endpoint= 'admin/api/2021-07/orders.json',
    status='any',
)
generate_active_order_df(
    records=active_orders,
    path='data_cache/active_order_cache.crypt',
)
# github_update(
#     file_path='data_cache/active_order_cache.crypt',
# )

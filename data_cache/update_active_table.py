# update_active_table.py
# Create db table of active subscription orders
# from Shopify API to reduce execution time in Dash app.

###########
# IMPORTS #
###########

# Import Packages #

from dotenv import load_dotenv
import os
import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.types import DateTime
import time

# Import .env variables #
load_dotenv()  # take environment variables from .env
SHOPIFY_PASSWORD = os.getenv('SHOPIFY_PASSWORD')
DATABASE_URL = os.getenv('DATABASE_URL')
# replace database_url prefix w/ 'postgresql' so sqlalchemy create_engine works
HEROKU_DB_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

#####################################
# Get Data from Shopify Order API ###
#####################################


def get_shopify_order_api(endpoint, status):
    '''Request and hold paginated data from the Shopify Order API

    Keyword arguments:
    status -- that status of the order('open', 'closed', 'cancelled', 'any')
    endpoint -- the target Shopify endpoint

    Reference:
    https://shopify.dev/api/admin/rest/reference/orders/order
    '''
    # Set URL
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_PASSWORD,
        "Content-Type": "application/json"
    }
    shop = "the-good-kitchen-esc.myshopify.com"
    endpoint = endpoint
    status = status
    limit = 250
    fields = 'email,order_number,created_at,cancelled_at,line_items'
    url = (f'https://{shop}/{endpoint}?fields={fields}&status={status}'
           f'&limit={limit}')

    # Access and store first page of results
    session = requests.Session()
    response = session.get(url, headers=headers)
    response_data = response.json()
    all_records = response_data['orders']

    # While Next Link is present, access and store next page
    count = 0
    while "next" in response.links:
        next_url = response.links["next"]["url"]
        response = session.get(next_url, headers=headers)
        count += 1
        # print(f'# of request cycles: {count}')
        response_data = response.json()
        all_records.extend(response_data['orders'])
        # Sleep to avoid rate limit if approach bucket size
        if response.headers['X-Shopify-Shop-Api-Call-Limit'] == '79/80':
            time.sleep(0.25)

    return all_records

#########


def generate_active_order_df(records):
    '''Create and store active order DataFrame in database

    Keyword arguments:
    records -- dictionary of records from API
    path -- file path to write encrypted DataFrame
    '''

    # Generate df from json and trim it to target
    # Keep active (non-cancelled) subscription orders.
    # Keep customer email, order number, order creation date,
    # subscription sku, and cancelled_at date.
    # Convert created_at to datetime
    df_orders_sub = pd.json_normalize(
        records,
        record_path='line_items',
        meta=['email', 'order_number', 'created_at', 'cancelled_at']
    )
    df_orders_sub = df_orders_sub.loc[:, ['email', 'order_number',
                                          'created_at', 'sku', 'cancelled_at']]
    df_orders_sub['created_at'] = pd.to_datetime(df_orders_sub['created_at'])
    df_orders_sub['sku'].fillna('No SKU', inplace=True)
    df_orders_sub = df_orders_sub[df_orders_sub['sku'].str.contains('SUB')]
    df_orders_sub = df_orders_sub[df_orders_sub['cancelled_at'].isnull()]

    # Convert DataFrame to sql and store in database
    engine = create_engine(HEROKU_DB_URL, echo=False)
    df_orders_sub.to_sql('active_sub',
                         con=engine,
                         if_exists='replace',
                         index=False,
                         dtype={'created_at': DateTime()}
                         )

##########################################
# Get active Shopify subscription orders #
##########################################


all_orders = get_shopify_order_api(
    endpoint='admin/api/2021-07/orders.json',
    status='any',
)
generate_active_order_df(
    records=all_orders
)

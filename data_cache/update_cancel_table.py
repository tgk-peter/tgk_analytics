# cancel_store.py
# Fetch cancelled subscription data from Recharge API and store in database
# to reduce execution time in Dash app.

###########
# IMPORTS #
###########

# Import Packages #
import pandas as pd
import requests
from sqlalchemy import create_engine
import time

# Import .env variables #
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
RECHARGE_API_TOKEN = os.getenv('RECHARGE_API_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

###########################################
# Get Data from Recharge Subscription API #
###########################################


def get_recharge_sub_api(status):
    '''Request and hold paginated data from the Recharge Subscription API

    Keyword arguments:
    status -- the status of the subscription ('ACTIVE', 'CANCELLED', 'EXPIRED')
    '''
    # Set request variables
    headers = {'X-Recharge-Access-Token': RECHARGE_API_TOKEN}
    status = status
    limit = 250

    # Access and store first page of subscription results
    # REMOVE CREATED_AT_MIN #
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


def generate_dataframe(records):
    '''Create and store cancellation DataFrame

    Keyword arguments:
    records -- dictionary of records from API
    '''
    # Create df from json results
    df = pd.json_normalize(records)

    # Keep columns customer email, when they cancelled,
    # the primary reason they cancelled, cancellation comments left.
    columns = ['email', 'cancelled_at', 'cancellation_reason',
               'cancellation_reason_comments']
    df_cancel = df.loc[:, columns]
    # Convert 'cancelled_at' values to datetime format.
    df_cancel['cancelled_at'] = pd.to_datetime(df_cancel['cancelled_at'])
    # Replace null in 'cancellation_reason' with 'None'
    df_cancel['cancellation_reason'].fillna('None', inplace=True)

    # Convert DataFrame to sql and store in database
    engine = create_engine(DATABASE_URL, echo=False)
    df_cancel.to_sql('cancel_db', con=engine, if_exists='replace', index=False)

# Get and store cancelled subscriptions #


cancellation_records = get_recharge_sub_api(
    status='CANCELLED'
)

generate_dataframe(
    records=cancellation_records
)

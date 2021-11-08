# cancel_store.py
# Fetch cancelled subscription data from Recharge API and store in database
# to reduce execution time in Dash app.

###########
# IMPORTS #
###########

# Import Packages #
from datetime import date, timedelta, datetime as dt
import numpy as np
import pandas as pd
import requests
from sqlalchemy import create_engine
import time

# Import .env variables #
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
DATABASE_URL = os.getenv('DATABASE_URL')
RECHARGE_API_TOKEN = os.getenv('RECHARGE_API_TOKEN')
YOTPO_X_GUID = os.getenv('YOTPO_X_GUID')
YOTPO_X_API_KEY = os.getenv('YOTPO_X_API_KEY')
# replace database_url prefix w/ 'postgresql' so sqlalchemy create_engine works
HEROKU_DB_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

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
    url = f'https://api.rechargeapps.com/subscriptions?status={status}&limit={limit}'
    response = requests.get(url, headers=headers)
    response_data = response.json()
    all_records = response_data['subscriptions']

    # # While Next Link is present, access and store next page
    # while 'next' in response.links:
    #     next_url = response.links['next']['url']
    #     response = requests.get(next_url, headers=headers)
    #     response_data = response.json()
    #     all_records.extend(response_data['subscriptions'])
    #     # Sleep to avoid rate limit if approach threshold
    #     if response.headers['X-Recharge-Limit'] == '39/40':
    #         time.sleep(0.5)

    return all_records


def get_yotpo_balance(customer_email):
    ''' Retrieve customer yotpo balance
    '''
    try:
        url = "https://loyalty.yotpo.com/api/v2/customers"
        querystring = {
            "customer_email": customer_email,
            "country_iso_code": "null",
            "with_referral_code": "false",
            "with_history": "false"
        }
        headers = {
            "Accept": "application/json",
            "x-guid": YOTPO_X_GUID,
            "x-api-key": YOTPO_X_API_KEY
        }
        result = requests.get(url, headers=headers, params=querystring)
        return result.json()["points_balance"]
    except KeyError:
        return 0


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
    # Lookup yotpo balance for cancelled_at < 90d
    cutoff_day = pd.Timestamp('now').floor('D') - pd.Timedelta(10, unit='D')
    df_cancel['yotpo_point_balance'] = df_cancel.apply(
        lambda row: get_yotpo_balance(row['email']) if row['cancelled_at'] > cutoff_day else 0,
        axis=1
        )

    # # Convert DataFrame to sql and store in database
    # engine = create_engine(HEROKU_DB_URL, echo=False)
    # df_cancel.to_sql('cancel_db', con=engine, if_exists='replace', index=False)

    print(df_cancel[['email', 'cancelled_at', 'yotpo_point_balance']])

# Get and store cancelled subscriptions #


cancellation_records = get_recharge_sub_api(
    status='CANCELLED'
)

generate_dataframe(
    records=cancellation_records
)

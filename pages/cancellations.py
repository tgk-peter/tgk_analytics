### Import Packages ###
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import requests
import json
import time
import pandas as pd
from datetime import date, timedelta, datetime as dt

### Import .env variables
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
RECHARGE_API_TOKEN = os.getenv('RECHARGE_API_TOKEN')

### Import Dash Instance ###
from app import app

### Access and Store Cancelled Subscriptions from Recharge ###
# Set request variables
headers = {"X-Recharge-Access-Token": RECHARGE_API_TOKEN}
status = "CANCELLED"
limit = 250

# Access and store first page of results

# Keep results short for testing. Uncomment when done.
#url = f"https://api.rechargeapps.com/subscriptions?status={status}&limit={limit}"
url = f"https://api.rechargeapps.com/subscriptions?status={status}&limit={limit}&created_at_min=2021-03-01"

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

## DataFrame for view and time slice

# Create a new dataframe that keeps customer email, when they cancelled,
# the primary reason they cancelled, and the cancellation comments they left.

columns = ["email", "cancelled_at", "cancellation_reason",
            "cancellation_reason_comments"]
df_cancel = df.loc[:, columns]
# Convert 'cancelled_at' values to datetime format.
df_cancel["cancelled_at"] = pd.to_datetime(df_cancel["cancelled_at"])

### Cancellation Layout and Callbacks ###
layout = html.Div(
    children=[
        html.H1(
            children='Cancellations',
        ),
        dcc.DatePickerRange(
            id='date-picker-range',
            min_date_allowed=date(2019, 6, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date.today(),
            start_date=pd.Timestamp('now').floor('D') - pd.Timedelta(7, unit="D"),
            end_date=pd.Timestamp('today').floor('D'),
        ),
        html.Div(id="cancel_counts_container"),
        dcc.Markdown('''
            # Cancellation Reasons
            When provided, here are the cancellation reason comments:
        '''),
        html.Div(id="cancel_reasons_container"),
    ]
)
# Update cancel counts container with table
@app.callback(
    Output(
        component_id='cancel_counts_container',
        component_property='children',
    ),
    [Input(
        component_id='date-picker-range',
        component_property='start_date',
    ),
    Input(
        component_id='date-picker-range',
        component_property='end_date',
    )]
)
def update_count_table(start_date, end_date):

    # Time slice
    cancelled_at_min = start_date
    cancelled_at_max = end_date
    date_range = (df_cancel["cancelled_at"] > cancelled_at_min)\
            & (df_cancel["cancelled_at"] < cancelled_at_max)
    df_cancel_2= df_cancel.loc[date_range]

    ## DataFrame for cancellation value counts and rename columns
    df_cancel_counts = df_cancel_2["cancellation_reason"].value_counts().to_frame().reset_index()
    df_cancel_counts.rename(columns={"index":"Reason", "cancellation_reason":"Count"}, inplace=True)
    return dbc.Table.from_dataframe(
        df = df_cancel_counts,
        id = "cancel_counts",
        striped=True,
        bordered=True,
        hover=True,
    )

# Update cancel reasons table
@app.callback(
    Output(
        component_id='cancel_reasons_container',
        component_property='children',
    ),
    [Input(
        component_id='date-picker-range',
        component_property='start_date',
    ),
    Input(
        component_id='date-picker-range',
        component_property='end_date',
    )]
)
def update_reason_table(start_date, end_date):

    # Time slice
    cancelled_at_min = start_date
    cancelled_at_max = end_date
    date_range = (df_cancel["cancelled_at"] > cancelled_at_min)\
            & (df_cancel["cancelled_at"] < cancelled_at_max)
    df_cancel_3= df_cancel.loc[date_range]

    ## Dataframe for non-empty reasons
    reasons_not_empty = (df_cancel_3["cancellation_reason_comments"].notnull()) \
                        & (df_cancel_3["cancellation_reason_comments"] != "")
    df_cancel_reasons = df_cancel_3.loc[reasons_not_empty]
    df_cancel_reasons = df_cancel_reasons.sort_values(by="cancelled_at", ascending=False)

    ## Return table with DataFrame
    return dbc.Table.from_dataframe(
        df = df_cancel_reasons,
        id = "cancel_reasons",
        striped=True,
        bordered=True,
        hover=True,
    )

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

from config import recharge_api_token

### Import Dash Instance ###
#from app import app

### Dash instance ###
external_stylesheets = [dbc.themes.UNITED]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

### Access and Store Cancelled Subscriptions from Recharge ###
# Set request variables
headers = {"X-Recharge-Access-Token": recharge_api_token}
status = "CANCELLED"
limit = 250

# Access and store first page of results
url = f"https://api.rechargeapps.com/subscriptions?status={status}&limit={limit}"
result = requests.get(url, headers=headers)
result_data = result.json()
total_results = result_data['subscriptions']
'''
# While Next Link is present, access and store next page
while "next" in result.links:
  next_url = result.links["next"]["url"]
  result = requests.get(next_url, headers=headers)
  result_data = result.json()
  total_results.extend(result_data['subscriptions'])
  # Sleep to avoid rate limit if approach threshold
  if result.headers['X-Recharge-Limit'] == '39/40':
    time.sleep(0.5)
'''
### Create DataFrames ###

## All data
df = pd.json_normalize(total_results)

## View w/ relevant columns
# Create a new dataframe that keeps customer id, when they cancelled,
#the primary reason they cancelled, and the cancellation comments they left.
# Convert 'cancelled_at' values to datetime format.
columns = ["customer_id", "cancelled_at", "cancellation_reason",
            "cancellation_reason_comments"]
df_view = df.loc[:, columns]
df_view["cancelled_at"] = pd.to_datetime(df_view["cancelled_at"])

## DataFrame for a time slice
cancelled_at_min = pd.Timestamp('now').floor('D') - pd.Timedelta(7, unit="D")
cancelled_at_max = pd.Timestamp('today').floor('D')
mask = (df_view["cancelled_at"] > cancelled_at_min)\
        & (df_view["cancelled_at"] < cancelled_at_max)
df_time_slice = df_view.loc[mask]

# DataFrame for cancellation reason counts
df_time_slice_counts = df_time_slice["cancellation_reason"].value_counts().to_frame().reset_index()
df_time_slice_counts.rename(columns={"index":"Reason", "cancellation_reason":"Count"}, inplace=True)
#df_time_slice_counts["% of total"] = df_time_slice_counts["Count"] / df_time_slice_counts["Count"].sum()*100

# DataFrame for cancellation reasons
reasons_not_empty = (df_time_slice["cancellation_reason_comments"].notnull()) \
                    & (df_time_slice["cancellation_reason_comments"] != "")
df_time_slice_reasons = df_time_slice.loc[reasons_not_empty]
df_time_slice_reasons = df_time_slice_reasons.sort_values(by="cancelled_at", ascending=False)

### Cancellation Layout and Callbacks ###
app.layout = html.Div(
    children=[
        html.H1(
            children='Cancellations',
        ),
        dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=date(2019, 6, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date.today(),
            start_date=date.today() - timedelta(days=7),
            end_date=date.today(),
        ),
        dbc.Table.from_dataframe(
            df = df_time_slice_counts,
            id = "table_counts",
            striped=True,
            bordered=True,
            hover=True,
        ),
        dcc.Markdown('''
            When provided, here are the cancellation reason comments:
        '''),
        dbc.Table.from_dataframe(
            df = df_time_slice_reasons,
            id = "table_reasons",
            striped=True,
            bordered=True,
            hover=True,
        ),
    ]
)
'''
@app.callback(
    Output(
        component_id='table_counts',
        component_property='df',
    ),
    [Input(
        component_id='page-2-radios',
        component_property='value',
    )]
)
def page_2_radios(value):
    return 'You have selected "{}"'.format(value)
'''
### Development Server
if __name__ == '__main__':
    app.run_server(debug=True)

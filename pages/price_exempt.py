# Use as template for new pages #

# IMPORTS #
# Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


# ENV imports
from dotenv import load_dotenv
import os

# Other
from datetime import date, timedelta, datetime as dt
import pandas as pd
import pytz
import requests

# Import .env variables
load_dotenv()  # take environment variables from .env
RECHARGE_API_TOKEN = os.getenv('RECHARGE_API_TOKEN')

# Import Dash Instance #
from app import app

# DATAFRAME #
# Get upcoming charges


def get_recharge_charges(date_min, date_max, limit=250, status='QUEUED'):
    ''' Get charges from Recharge API

        limit - The amount of results. Maximum is 250, default is 50.
        status - Filter charges by status. Available status:
                 SUCCESS, QUEUED, ERROR, REFUNDED, PARTIALLY_REFUNDED, SKIPPED
        date_min - Show charges scheduled after the given date.
        date_max - Show charges scheduled before the given date.
    '''
    headers = {'X-Recharge-Access-Token': RECHARGE_API_TOKEN}
    url = (f'https://api.rechargeapps.com/charges?limit={limit}&status={status}'
           f'&date_min={date_min}&date_max={date_max}')

    response = requests.get(url, headers=headers)
    charge_data = response.json()['charges']
    return charge_data


# get charges scheduled for tomorrow through 2 days out
charge_get = get_recharge_charges(
             date_min=(date.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
             date_max=(date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
)

# Create df from data. Create empty df if no charges in que.
df_charge = pd.json_normalize(charge_get)
try:
    df_charge = df_charge[['address_id', 'scheduled_at', 'total_price',
                           'email', 'first_name', 'last_name']]
except KeyError:
    df_charge = pd.DataFrame(columns=['address_id', 'scheduled_at',
                                      'total_price', 'email', 'first_name',
                                      'last_name'])

# Load price exempt customer df
exempt_path = 'data_cache/price_exempt_all.csv'
df_exempt = pd.read_csv(exempt_path)

# Compare to price exempt list and keep only those customers
df_exempt_que = df_charge[df_charge['email'].isin(df_exempt['email'])]
df_exempt_que.columns = ['Address ID', 'Date Scheduled', 'Total Price', 'Customer Email', 'First Name', 'Last Name']


# PAGE LAYOUT #
# Layout components
active_exempt_table = dbc.Table.from_dataframe(
    df=df_exempt_que,
    id='active_exempt',
    striped=True,
    bordered=True,
    hover=True,
    responsive=True,
)

markdown = dcc.Markdown('''
    # Price Increase Exempt Customers
    Customers with qued charges that are exempt from price increase.
    ''')

# update timestamp for eastern timezone
#update_time = dt.now(pytz.timezone('America/New_York')).strftime('%c')
update_time = dt.now(pytz.timezone('America/New_York')).strftime('%b %d, %Y %I:%M%p')
#update_time = dt.now().strftime('%b %m, %Y %I:%M%p')

# Layout
layout = dbc.Container(
    children=[
        dbc.Row(dbc.Col(markdown)),
        dbc.Row(dbc.Col(f'Last updated: {update_time}')),
        dbc.Row(dbc.Col(active_exempt_table)),
        html.Div(
            id='page-1-content',
        ),
    ]
)

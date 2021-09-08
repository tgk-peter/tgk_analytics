# Use as template for new pages #

# IMPORTS #
# Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash_table import DataTable

# ENV imports
from dotenv import load_dotenv
import os

# Other
from datetime import date, timedelta
import json
import pandas as pd
import requests

# Import .env variables
load_dotenv()  # take environment variables from .env
RECHARGE_API_TOKEN = os.getenv('RECHARGE_API_TOKEN')

# Dash instance #
# For isolated development purposes only, remove this section when ready
# to link to index
external_stylesheets = [dbc.themes.UNITED]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Import Dash Instance #
# Uncomment when ready to link to index page
#from app import app

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
    headers = {"X-Recharge-Access-Token": RECHARGE_API_TOKEN}
    url = f"https://api.rechargeapps.com/charges?limit={limit}&status={status}&date_min={date_min}&date_max={date_max}"

    response = requests.get(url, headers=headers)
    charge_data = response.json()['charges']
    return charge_data


# get charges scheduled for tomorrow through 2 days out
charge_get = get_recharge_charges(
             date_min=(date.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
             date_max=(date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
)

# Create df from data
df_charge = pd.json_normalize(charge_get)
df_charge = df_charge[['address_id', 'scheduled_at', 'total_price', 'email',
                      'first_name', 'last_name']]

# Load price exempt customer df
exempt_path = '../data_cache/price_exempt_all.csv'
df_exempt = pd.read_csv(exempt_path)

# Compare to price exempt list and keep only those customers
df_exempt_que = df_charge[df_charge['email'].isin(df_exempt['email'])]
df_exempt_que.columns = ['Address ID', 'Date Scheduled', 'Total Price', 'Customer Email', 'First Name', 'Last Name']


# PAGE LAYOUT #

active_exempt_table = DataTable(
    id='active_exempt',
    columns=[{"name": i, "id": i} for i in df_exempt_que.columns],
    data=df_exempt_que.to_dict('records'),
    # page_size=26,
    style_cell={'textAlign': 'center', 'fontSize': 16, 'font-family': 'Ubuntu'},
    filter_action='native',
    # style_data_conditional=conditional_style_all,
)

active_exempt_table_2 = dbc.Table.from_dataframe(
    df=df_exempt_que,
    id="cancel_customers",
    striped=True,
    bordered=True,
    hover=True,
    responsive=True,
)

# delete 'app.' when ready to link to index page
app.layout = dbc.Container(
    children=[
        dbc.Row(dbc.Col(dcc.Markdown('''
        # Pricing Exempt Customers
        Customers with qued charges that are exempt from price increase.
        '''))),
        active_exempt_table,
        active_exempt_table_2,
        html.Div(
            id='page-1-content',
        ),
    ]
)

# PAGE CALLBACKS #
'''
@app.callback(
    Output(
        component_id='page-1-content',
        component_property='children',
    ),
    Input(
        component_id='page-1-dropdown',
        component_property='value',
    )
)
def page_1_dropdown(value):
    return 'You have selected "{}"'.format(value)
'''

# Development Server
# For isolated development purposes only, remove this section when ready
# to link to index
if __name__ == '__main__':
    app.run_server(debug=True)

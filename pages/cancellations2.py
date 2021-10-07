# cancellations2.py #
# monthly count of cancellation reasons #

# Import Packages #
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import plotly.express as px

import pandas as pd
import psycopg2
import cryptpandas as crp

from dotenv import load_dotenv
import os

# Import .env variables #
load_dotenv()  # take environment variables from .env
CRP_PASSWORD = os.getenv('CRP_PASSWORD')
DATABASE_URL = os.getenv('DATABASE_URL')

# Import Dash Instance #
from app import app

# DATAFRAMES #
# Decrypt and load cancelled subscription dataframe
# Load cancelled subscription dataframe from database #
con = psycopg2.connect(DATABASE_URL)
cur = con.cursor()
query = f"""SELECT *
            FROM cancel_db
            """
df_cancel = pd.read_sql(query, con)
con.close()

# restrict to after 06/01/2019
df_cancel = df_cancel[df_cancel['cancelled_at'] > '2019-06-01']

# Group by month and cancellation reason. Count emails.
df_cancel_agg_grp = df_cancel.groupby(
    [pd.Grouper(key='cancelled_at', freq='MS'), 'cancellation_reason'])
df_cancel_agg = df_cancel_agg_grp.agg(cancel_count=('email', 'count'))
df_cancel_agg.reset_index(inplace=True)
df_cancel_agg['month_cancel_total'] = \
    df_cancel_agg.groupby('cancelled_at')['cancel_count'].transform('sum')
df_cancel_agg['percent_total'] = \
    df_cancel_agg['cancel_count'] / df_cancel_agg['month_cancel_total']

# LAYOUT #

# Month Rangeslider
month_list = df_cancel_agg['cancelled_at'].dt.strftime('%b %Y').unique()
mark_style = {'font-family': 'Ubuntu', 'writing-mode': 'vertical-rl',
              'white-space': 'nowrap'}
month_slider = dcc.RangeSlider(
    id='month_slider',
    min=0,
    max=len(month_list) - 1,
    step=None,
    marks={k: {'label': v, 'style': mark_style}
           for (k, v) in enumerate(month_list)},
    value=[0, len(month_list) - 1],
)

# Page Layout
layout = html.Div(
    children=[
        dcc.Store(id='df_output'),
        html.H1('Cancellations over Time'),
        dbc.Row(
            children=dbc.Col(
                children=month_slider,
                className='mb-4',
                ),
            className='border mb-3 pb-5 pt-3',
        ),
        dbc.Row(
            children=dbc.Col(dcc.Graph(id='count_graph')),
            className='border mb-3',
        ),
        dbc.Row(
            children=dbc.Col(dcc.Graph(id='count_bar')),
            className='border mb-3',
        ),
        dbc.Row(
            children=dbc.Col(dcc.Graph(id='count_normalize_bar')),
            className='border mb-3',
        ),
    ]
)

# CALLBACKS #


@app.callback(
    Output(
        component_id='df_output',
        component_property='data',
    ),
    Input(
        component_id='month_slider',
        component_property='value',
    )
)
def df_store(value):
    ''' Update dcc.Store that all graphs access
    '''
    months = df_cancel_agg['cancelled_at'].dt.strftime('%Y-%m-%d').unique()
    switcher = {k: v for k, v in enumerate(months)}
    cancelled_at_min = switcher.get(value[0])
    cancelled_at_max = switcher.get(value[1])
    date_range = (df_cancel_agg["cancelled_at"] >= cancelled_at_min)\
        & (df_cancel_agg["cancelled_at"] <= cancelled_at_max)
    df_cancel_slice = df_cancel_agg.loc[date_range]
    return df_cancel_slice.to_dict('records')


@app.callback(
    Output(
        component_id='count_graph',
        component_property='figure',
    ),
    Input(
        component_id='df_output',
        component_property='data',
    )
)
def update_count_line(data):
    count_line = px.line(
        data_frame=data,
        x='cancelled_at',
        y='cancel_count',
        color='cancellation_reason',
        title='Cancellation Counts Over Time - Individual Reasons',
        labels={
            'cancel_count': 'Cancellations',
            'cancelled_at': 'Month',
            'cancellation_reason': 'Reason',
        },
        height=620,
    )
    return count_line


@app.callback(
    Output(
        component_id='count_bar',
        component_property='figure',
    ),
    Input(
        component_id='df_output',
        component_property='data',
    )
)
def update_count_bar(data):
    count_bar = px.bar(
        data_frame=data,
        x='cancelled_at',
        y='cancel_count',
        color='cancellation_reason',
        title='Cancellation Counts Over Time - Stacked',
        labels={
            'cancel_count': 'Cancellations',
            'cancelled_at': 'Month',
            'cancellation_reason': 'Reason',
        },
        height=620,
    )
    return count_bar


@app.callback(
    Output(
        component_id='count_normalize_bar',
        component_property='figure',
    ),
    Input(
        component_id='df_output',
        component_property='data',
    )
)
def update_count_bar_norm(data):
    count_normalize_bar = px.bar(
        data_frame=data,
        x='cancelled_at',
        y='percent_total',
        color='cancellation_reason',
        title='Cancellation Counts Over Time - Percentage',
        labels={
            'percent_total': '% of Cancellations',
            'cancelled_at': 'Month',
            'cancellation_reason': 'Reason',
        },
        height=620,
    )
    count_normalize_bar.update_layout(
        yaxis={'tickformat': '%'}  # format yaxis to percentage
    )
    return count_normalize_bar

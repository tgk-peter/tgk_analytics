# cancellations2.py #
# monthly count of cancellation reasons #

# Import Packages #
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import plotly.express as px

import pandas as pd
from datetime import date, timedelta, datetime as dt
import cryptpandas as crp

from dotenv import load_dotenv
import os

# Import .env variables #
load_dotenv()  # take environment variables from .env
CRP_PASSWORD = os.getenv('CRP_PASSWORD')

# Import Dash Instance #
# Uncomment when ready to link to index page
from app import app

###### TEST DATA ######
data = {
    'Too Many Meals': [95, 75, 85, 65, 60],
    'Not Happy with Quality': [80, 90, 45, 55, 75],
    'Other': [106, 77, 92, 74, 65],
}

indx = [
    'January 2021',
    'February 2021',
    'March 2021',
    'April 2021',
    'May 2021',
]

df_counts = pd.DataFrame(data, index=indx)

df_normalize = df_counts.div(df_counts.sum(axis=1), axis=0)

df_normalize_2 = df_normalize.transpose()

# DATAFRAMES #
# Decrypt and load cancelled subscription dataframe
df_cancel = crp.read_encrypted(path='data_cache/cancel_sub_cache.crypt', \
            password=CRP_PASSWORD)

# Group by month and cancellation reason. Count emails.
df_cancel_agg = df_cancel.groupby([pd.Grouper(key='cancelled_at', freq='MS'), 'cancellation_reason']).agg({'email':'count'})
df_cancel_agg.reset_index(inplace=True)


# Cancellation 2 Layout #

# layout components
count_fig = px.line(
    data_frame=df_counts,
    title='Cancellation Counts Over Time',
    labels={
        'value': 'Cancellations',
        'index': 'Month',
        'variable': 'Reason',
    },
)

normalize_fig = px.bar(
    data_frame=df_normalize,
)

normalize_table = dbc.Table.from_dataframe(
    df=df_normalize_2.reset_index(),
    id="normalize_table",
    striped=True,
    bordered=True,
    hover=True,
    responsive=True,
)

checklist = dbc.FormGroup(
    [
        dbc.Label("Choose Reasons (input options)"),
        dbc.Checklist(
            options=[
                {"label": "Too Many Meals", "value": 1},
                {"label": "Not Happy with Quality", "value": 2},
                {"label": "Other", "value": 3},
            ],
            value=[1],
            id="checklist-input",
        ),
    ]
)

# Month Rangeslider
month_list = df_cancel_agg['cancelled_at'].dt.strftime('%b %Y').unique()
month_slider = dcc.RangeSlider(
    id='month_slider',
    min=0,
    max=len(month_list) - 1,
    step=None,
    marks={k: {'label': v, 'style': {'font-family': 'Ubuntu', 'writing-mode': 'vertical-rl', 'white-space': 'nowrap'}} for (k, v) in enumerate(month_list)},
    value=[0, len(month_list) - 1],
)

# Layout
layout = html.Div(
    children=[
        html.H1(
            children='Cancellations 2',
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        month_slider,
                    ],
                    className='mb-4',
                )
            ],
            className='border mb-3 pb-5 pt-3',
        ),
        html.Div(
            id='rangeslider_out'
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dcc.Graph(
                            id='count_graph',
                            figure=count_fig,
                        ),
                    ],
                )
            ],
            className='border mb-3',
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        checklist,
                    ],
                )
            ],
            className='border mb-3',
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dcc.Graph(
                            id='normalize_graph',
                            figure=normalize_fig,
                        ),
                    ],
                )
            ],
            className='border mb-3',
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        normalize_table,
                    ],
                )
            ],
            className='border mb-3',
        ),
    ]
)
'''
### Page 1 Callbacks ###
@app.callback(
    Output(
        component_id='rangeslider_out',
        component_property='children',
    ),
    [Input(
        component_id='month_slider',
        component_property='value',
    )]
)
def page_1_dropdown(value):
    start_month = value[0]
    end_month = value[-1]
    return f'Start month is {start_month} and end month is {end_month}.'
'''

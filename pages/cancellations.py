### Import Packages ###
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
import requests
import json
import time
import pandas as pd
from datetime import date, timedelta, datetime as dt
import cryptpandas as crp

### Import .env variables
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
CRP_PASSWORD = os.getenv('CRP_PASSWORD')

### Import Dash Instance ###
from app import app

# Decrypt and load cancelled subscription dataframe
df_cancel = crp.read_encrypted(path='data_cache/cancel_sub_cache.crypt', password=CRP_PASSWORD)

### Cancellation Layout ###
layout = html.Div(
    children=[
        html.H1(
            children='Cancellations',
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dcc.DatePickerRange(
                            id='date-picker-range',
                            min_date_allowed=date(2019, 6, 1),
                            max_date_allowed=date.today(),
                            initial_visible_month=date.today(),
                            start_date=pd.Timestamp('now').floor('D') - pd.Timedelta(7, unit="D"),
                            end_date=pd.Timestamp('today').floor('D'),
                        ),
                    ],
                ),
                dbc.Col(
                    children=[
                        html.Div(
                            children='',
                            id='cancel_total_box',
                            className='pt-2',
                        ),
                    ],
                    width='auto',
                    className='border',
                ),
            ],
            className='mb-3 mr-1',
        ),
        dbc.Card(
            children=[
                dbc.CardBody(
                    children=[
                        html.H4(
                            children=[
                                "Cancellation Counts"
                            ],
                            className='card-title',
                        ),
                        html.P(
                            children=[
                                "This table contains information for all \
                                cancelled subscriptions within the selected \
                                date range. It shows a list of each cancellation \
                                reason and the number of times it occured."
                            ],
                            className='card-text'
                        ),
                        dbc.Spinner(
                            children=[
                                html.Div(
                                    id="cancel_counts_container",
                                ),
                            ],
                            color='primary',
                        ),
                    ],
                ),
            ],
            color='secondary',
            outline=True,
            className='mb-3',
        ),
        dbc.Card(
            children=[
                dbc.CardBody(
                    children=[
                        html.H4(
                            children=[
                                'Cancellation Reason Comments'
                            ],
                            className='card-title',
                        ),
                        html.P(
                            children=[
                                'All customers are required to enter a \
                                cancellation reason. They can optionally leave \
                                a cancellation comment. When provided, here are \
                                the cancellation reason comments.'
                            ],
                            className='card-text',
                        ),
                        dbc.Button(
                            children=[
                                'Download CSV'
                            ],
                            id='btn_reason_csv',
                            color='primary',
                            className='mb-3',
                        ),
                        Download(
                            id='download_reason_csv',
                        ),
                        html.Div(id="cancel_reasons_container"),
                    ],
                ),
            ],
            color='secondary',
            outline=True,
            className='mb-3',
        ),
        dbc.Card(
            children=[
                dbc.CardBody(
                    children=[
                        html.H4(
                            children=[
                                'Customers by Cancellation Reason',
                            ],
                            className='card-title',
                        ),
                        html.P(
                            children=[
                                'This table lists all of the customers that \
                                indicated a particular cancellation reason \
                                when they cancelled.'
                            ],
                            className='card-text',
                        ),
                        dcc.Dropdown(
                            id='reason-dropdown',
                            options=[{'label': i, 'value': i} for i in df_cancel \
                            ['cancellation_reason'].unique()],
                            placeholder='Select a reason',
                            className='mb-2',
                        ),
                        dbc.Spinner(
                            children=[
                                html.Div(id="customers_by_reason_container"),
                            ],
                            color='primary',
                        ),
                    ],
                ),
            ],
            color='secondary',
            outline=True,
            className='mb-3',
        ),
    ]
)
### Cancellation Callbacks ###
## Function to slice by time
def time_slice(start_date, end_date):
    cancelled_at_min = start_date
    cancelled_at_max = end_date
    date_range = (df_cancel["cancelled_at"] > cancelled_at_min)\
            & (df_cancel["cancelled_at"] < cancelled_at_max)
    df_cancel_slice = df_cancel.loc[date_range]
    return df_cancel_slice

## Update cancellation total display
@app.callback(
    Output(
        component_id='cancel_total_box',
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
def update_total_cancels(start_date, end_date):
    df_cancel_slice = time_slice(start_date, end_date)
    df_cancel_total = df_cancel_slice["cancellation_reason"].value_counts().sum()
    return html.H5(f'Total Cancellations = {df_cancel_total}')

## Update cancel counts container with table
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
    df_cancel_slice = time_slice(start_date, end_date)
    df_cancel_counts = df_cancel_slice["cancellation_reason"].value_counts().to_frame().reset_index()
    df_cancel_counts.rename(columns={"index":"Reason", "cancellation_reason":"Count"}, inplace=True)
    return dbc.Table.from_dataframe(
        df = df_cancel_counts,
        id = "cancel_counts",
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )

## Update cancel reasons table
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
    df_cancel_slice = time_slice(start_date, end_date)

    ## Dataframe for non-empty reasons
    reasons_not_empty = (df_cancel_slice["cancellation_reason_comments"].notnull()) \
                        & (df_cancel_slice["cancellation_reason_comments"] != "")
    df_cancel_reasons = df_cancel_slice.loc[reasons_not_empty]
    df_cancel_reasons = df_cancel_reasons.sort_values(by="cancelled_at", ascending=False)

    ## Return table with DataFrame
    return dbc.Table.from_dataframe(
        df = df_cancel_reasons,
        id = "cancel_reasons",
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )

## Cancel reasons download csv
@app.callback(
    Output(
        component_id='download_reason_csv',
        component_property='data',
    ),
    [Input(
        component_id='date-picker-range',
        component_property='start_date',
    ),
    Input(
        component_id='date-picker-range',
        component_property='end_date',
    ),
    Input(
        component_id='btn_reason_csv',
        component_property='n_clicks',
    )],
    prevent_initial_call=True,
)
def download_reason_csv(start_date, end_date, n_clicks):
    df_cancel_slice = time_slice(start_date, end_date)

    ## Dataframe for non-empty reasons
    reasons_not_empty = (df_cancel_slice["cancellation_reason_comments"].notnull()) \
                            & (df_cancel_slice["cancellation_reason_comments"] != "")
    df_cancel_reasons = df_cancel_slice.loc[reasons_not_empty]
    df_cancel_reasons = df_cancel_reasons.sort_values(by="cancelled_at", ascending=False)

    return send_data_frame(df_cancel_reasons.to_csv, f"cancel_comments_{start_date}_{end_date}.csv")

## Update customers by cancel reason table
@app.callback(
    Output(
        component_id='customers_by_reason_container',
        component_property='children',
    ),
    [Input(
        component_id='date-picker-range',
        component_property='start_date',
    ),
    Input(
        component_id='date-picker-range',
        component_property='end_date',
    ),
    Input(
        component_id='reason-dropdown',
        component_property='value',
    )]
)
def update_customer_by_reason_table(start_date, end_date, reason):
    df_cancel_slice = time_slice(start_date, end_date)

    ## Dataframe for customers by reason
    reason = df_cancel_slice["cancellation_reason"] == reason
    df_cancel_customers = df_cancel_slice.loc[reason]
    df_cancel_customers = df_cancel_customers.loc[:, ["email", "cancelled_at", "cancellation_reason"]]
    df_cancel_customers = df_cancel_customers.sort_values(by="cancelled_at", ascending=False)

    ## Return table with DataFrame
    return dbc.Table.from_dataframe(
        df = df_cancel_customers,
        id = "cancel_customers",
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )

# IMPORTS #
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame

from datetime import date  # , timedelta, datetime as dt
from dotenv import load_dotenv
import os
import pandas as pd
import psycopg2
import requests

# Import .env variables

load_dotenv()  # take environment variables from .env
DATABASE_URL = os.getenv('DATABASE_URL')
# replace database_url prefix w/ 'postgresql' so sqlalchemy create_engine works
HEROKU_DB_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

# Import Dash Instance #
from app import app

# DATAFRAME #
# Load cancelled subscription dataframe from database #
con = psycopg2.connect(HEROKU_DB_URL)
cur = con.cursor()
query = f"""SELECT *
            FROM cancel_db
            """
df_cancel = pd.read_sql(query, con)
con.close()

# LAYOUT #

# Layout Components
datepicker_range = dcc.DatePickerRange(
    id='date-picker-range',
    min_date_allowed=date(2019, 6, 1),
    max_date_allowed=date.today(),
    initial_visible_month=date.today(),
    start_date=pd.Timestamp('now').floor('D') - pd.Timedelta(7, unit="D"),
    end_date=pd.Timestamp('today').floor('D'),
)

dropdown = dcc.Dropdown(
    id='reason-dropdown',
    options=[{'label': 'All Reasons', 'value': 'All Reasons'}] +
            [{'label': i, 'value': i} for i in df_cancel['cancellation_reason'].drop_duplicates().sort_values()],
    placeholder='Select a reason',
    className='mb-2',
)

# Page layout
layout = html.Div(
    children=[
        dcc.Store(id='df_cancel_slice'),
        html.H1('Cancellations'),
        dbc.Row(
            children=[
                dbc.Col(datepicker_range),
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
                        dbc.Button(
                            children=[
                                'Download CSV'
                            ],
                            id='btn_reason_indiv_csv',
                            color='primary',
                            className='mb-3',
                        ),
                        Download(
                            id='dl_reason_indiv_csv',
                        ),
                        dropdown,
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
# CALLBACKS #

# Helper functions


def time_slice(start_date, end_date):
    '''Filter DataFrame by date range

    Keyword arguments:
    start_date -- beginning of date range
    end_date -- end of date range
    '''
    cancelled_at_min = start_date
    cancelled_at_max = end_date
    date_range = (df_cancel["cancelled_at"] > cancelled_at_min)\
        & (df_cancel["cancelled_at"] < cancelled_at_max)
    df_cancel_slice = df_cancel.loc[date_range]
    return df_cancel_slice


def df_non_empty(df_cancel_slice):
    ''' Create DataFrame for non-empty reasons
    '''
    reasons_not_empty = (df_cancel_slice["cancellation_reason_comments"].notnull()) \
        & (df_cancel_slice["cancellation_reason_comments"] != "")
    df_cancel_reasons = df_cancel_slice.loc[reasons_not_empty]
    df_cancel_reasons = df_cancel_reasons.sort_values(by="cancelled_at",
                                                      ascending=False)
    return df_cancel_reasons


# CALLBACKS


@app.callback(
    Output(
        component_id='df_cancel_slice',
        component_property='data',
    ),
    Input(
        component_id='date-picker-range',
        component_property='start_date',
    ),
    Input(
        component_id='date-picker-range',
        component_property='end_date',
    )
)
def df_store(start_date, end_date):
    ''' Update dcc.Store(id=df_cancel_slice)
    '''
    df_cancel_slice = time_slice(start_date, end_date)
    df_cancel_reasons = df_non_empty(df_cancel_slice=df_cancel_slice)
    dataframes = {
        'df_cancel_slice': df_cancel_slice.to_dict('records'),
        'df_cancel_reasons': df_cancel_reasons.to_dict('records'),
    }
    return dataframes


@app.callback(
    Output(
        component_id='cancel_total_box',
        component_property='children',
    ),
    Input(
        component_id='df_cancel_slice',
        component_property='data',
    )
)
def update_total_cancels(data):
    ''' Update cancellation total display
    '''
    df_cancel_slice = pd.DataFrame.from_dict(data['df_cancel_slice'])
    df_cancel_total = df_cancel_slice["cancellation_reason"].value_counts().sum()
    return html.H5(f'Total Cancellations = {df_cancel_total}')


@app.callback(
    Output(
        component_id='cancel_counts_container',
        component_property='children',
    ),
    Input(
        component_id='df_cancel_slice',
        component_property='data',
    )
)
def update_count_table(data):
    ''' Update cancel counts container with table
    '''
    df_cancel_slice = pd.DataFrame.from_dict(data['df_cancel_slice'])
    df_cancel_counts = df_cancel_slice["cancellation_reason"].value_counts()\
        .to_frame().reset_index()
    df_cancel_counts.rename(
        columns={"index": "Reason", "cancellation_reason": "Count"},
        inplace=True
    )
    return dbc.Table.from_dataframe(
        df=df_cancel_counts,
        id="cancel_counts",
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )


@app.callback(
    Output(
        component_id='cancel_reasons_container',
        component_property='children',
    ),
    Input(
        component_id='df_cancel_slice',
        component_property='data',
    )
)
def update_reason_table(data):
    ''' Update cancel reasons table
    '''
    # Dataframe for non-empty reasons
    df_cancel_reasons = pd.DataFrame.from_dict(data['df_cancel_reasons'])
    df_cancel_reasons.rename(
        columns={
            "email": "Email",
            "cancelled_at": "Cancelled",
            "cancellation_reason": "Cancellation Reason",
            "cancellation_reason_comments": "Comments",
            "yotpo_point_balance": "Yotpo Points"
            },
        inplace=True
    )

    # Return table with DataFrame
    return dbc.Table.from_dataframe(
        df=df_cancel_reasons,
        id="cancel_reasons",
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )


@app.callback(
    Output(
        component_id='download_reason_csv',
        component_property='data',
    ),
    Input(
        component_id='btn_reason_csv',
        component_property='n_clicks',
    ),
    State(
        component_id='df_cancel_slice',
        component_property='data',
    ),
    prevent_initial_call=True,
)
def download_reason_csv(n_clicks, data):
    ''' Cancel reasons download csv
    '''
    # Dataframe for non-empty reasons
    df_cancel_reasons = pd.DataFrame.from_dict(data['df_cancel_reasons'])
    df_cancel_reasons.rename(
        columns={
            "email": "Email",
            "cancelled_at": "Cancelled",
            "cancellation_reason": "Cancellation Reason",
            "cancellation_reason_comments": "Comments",
            "yotpo_point_balance": "Yotpo Points"
            },
        inplace=True
    )

    return send_data_frame(df_cancel_reasons.to_csv,
                           f"cancel_comments.csv")


@app.callback(
    Output(
        component_id='customers_by_reason_container',
        component_property='children',
    ),
    Input(
        component_id='df_cancel_slice',
        component_property='data',
    ),
    Input(
        component_id='reason-dropdown',
        component_property='value',
    )
)
def update_customer_by_reason_table(data, value):
    ''' Update customers by cancel reason table
    '''
    df_cancel_slice = pd.DataFrame.from_dict(data['df_cancel_slice'])

    # Dataframe for customers by reason
    if value == 'All Reasons':
        df_cancel_customers = df_cancel_slice
    else:
        reason = df_cancel_slice["cancellation_reason"] == value
        df_cancel_customers = df_cancel_slice.loc[reason]
    df_cancel_customers = df_cancel_customers.sort_values(by="cancelled_at",
                                                          ascending=False)
    df_cancel_customers.rename(
        columns={
            "email": "Email",
            "cancelled_at": "Cancelled",
            "cancellation_reason": "Cancellation Reason",
            "cancellation_reason_comments": "Comments",
            "yotpo_point_balance": "Yotpo Points"
            },
        inplace=True
    )

    # Return table with DataFrame
    return dbc.Table.from_dataframe(
        df=df_cancel_customers,
        id="cancel_customers",
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )


@app.callback(
    Output(
        component_id='dl_reason_indiv_csv',
        component_property='data',
    ),
    Input(
        component_id='btn_reason_indiv_csv',
        component_property='n_clicks',
    ),
    State(
        component_id='reason-dropdown',
        component_property='value',
    ),
    State(
        component_id='df_cancel_slice',
        component_property='data',
    ),
    prevent_initial_call=True,
)
def download_reason_csv(n_clicks, value, data):
    ''' Individual cancel reason download csv
    '''
    df_cancel_slice = pd.DataFrame.from_dict(data['df_cancel_slice'])

    # Dataframe for customers by reason
    if value == 'All Reasons':
        df_cancel_customers = df_cancel_slice
    else:
        reason = df_cancel_slice["cancellation_reason"] == value
        df_cancel_customers = df_cancel_slice.loc[reason]
    df_cancel_customers = df_cancel_customers.sort_values(by="cancelled_at",
                                                          ascending=False)
    df_cancel_customers.rename(
        columns={
            "email": "Email",
            "cancelled_at": "Cancelled",
            "cancellation_reason": "Cancellation Reason",
            "cancellation_reason_comments": "Comments",
            "yotpo_point_balance": "Yotpo Points"
            },
        inplace=True
    )
    return send_data_frame(df_cancel_customers.to_csv,
                           f"cancel_reason.csv")

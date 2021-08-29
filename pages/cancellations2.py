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

#TEST DATA #
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
df_cancel = crp.read_encrypted(path='data_cache/cancel_sub_cache.crypt',
                               password=CRP_PASSWORD)
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

# Cancellation 2 Layout #

# layout components
# count_line = px.line(
#     data_frame=df_cancel_agg,
#     x='cancelled_at',
#     y='cancel_count',
#     color='cancellation_reason',
#     title='Cancellation Counts Over Time - Individual Reasons',
#     labels={
#         'cancel_count': 'Cancellations',
#         'cancelled_at': 'Month',
#         'cancellation_reason': 'Reason',
#     },
#     height=620,
# )

count_bar = px.bar(
    data_frame=df_cancel_agg,
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

count_normalize_bar = px.bar(
    data_frame=df_cancel_agg,
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
mark_style = {'font-family': 'Ubuntu', 'writing-mode': 'vertical-rl',
              'white-space': 'nowrap'}
month_slider = dcc.RangeSlider(
    id='month_slider',
    min=0,
    max=len(month_list) - 1,
    step=None,
    marks={k: {'label': v, 'style': mark_style}
           for (k, v) in enumerate(month_list)},
    # value=month_list,
    value=[0, len(month_list) - 1],
)

# Layout
layout = html.Div(
    children=[
        dcc.Store(id='df_output'),
        html.H1(
            children='Cancellations 2',
        ),
        dbc.Row(
            children=dbc.Col(
                children=month_slider,
                className='mb-4',
                ),
            className='border mb-3 pb-5 pt-3',
        ),
        html.Div(
            id='rangeslider_out'
        ),
        dbc.Row(
            children=dbc.Col(
                dcc.Graph(
                    id='count_graph',
                    # figure=count_line,
                ),
            ),
            className='border mb-3',
        ),
        # dbc.Row(
        #     children=[
        #         dbc.Col(
        #             children=[
        #                 checklist,
        #             ],
        #         )
        #     ],
        #     className='border mb-3',
        # ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dcc.Graph(
                            id='count_bar',
                            figure=count_bar,
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
                        dcc.Graph(
                            id='count_normalize_bar',
                            figure=count_normalize_bar,
                        ),
                    ],
                )
            ],
            className='border mb-3',
        ),
        # dbc.Row(
        #     children=[
        #         dbc.Col(
        #             children=[
        #                 normalize_table,
        #             ],
        #         )
        #     ],
        #     className='border mb-3',
        # ),
    ]
)

# Page 1 Callbacks ###


# def time_slice(start_date, end_date):
#     '''Filter DataFrame by date range
#
#     Keyword arguments:
#     start_date -- beginning of date range
#     end_date -- end of date range
#     '''
#     cancelled_at_min = start_date
#     cancelled_at_max = end_date
#     date_range = (df_cancel["cancelled_at"] > cancelled_at_min)\
#         & (df_cancel["cancelled_at"] < cancelled_at_max)
#     df_cancel_slice = df_cancel.loc[date_range]
#     return df_cancel_slice

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
    ''' Update dcc.Store
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
def update_count_graph(data):
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

# @app.callback(
#     Output(
#         component_id='rangeslider_out',
#         component_property='children',
#     ),
#     [Input(
#         component_id='month_slider',
#         component_property='value',
#     )]
# )
# def page_1_dropdown(value):
#     month_list = df_cancel_agg['cancelled_at'].dt.strftime('%Y-%m-%d').unique()
#     switcher = {k: v for k, v in enumerate(month_list)}
#     start_month = switcher.get(value[0])
#     end_month = switcher.get(value[1])
#     return f'Start month is {start_month} and end month is {end_month}.'

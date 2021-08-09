#### Use as template for new pages ####

### Import Packages ###
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import date, timedelta, datetime as dt
import cryptpandas as crp

### Import .env variables
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
CRP_PASSWORD = os.getenv('CRP_PASSWORD')

### Dash instance ###
# For isolated development purposes only, remove this section when ready
# to link to index
external_stylesheets = [dbc.themes.UNITED]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

### Import Dash Instance ###
# Uncomment when ready to link to index page
#from app import app

mock = {
    'Too Many Meals' : [95, 75, 85, 65, 60],
    'Not Happy with Quality' : [80, 90, 45, 55, 75],
}

indx = [
    'January 2021',
    'February 2021',
    'March 2021',
    'April 2021',
    'May 2021'
]

df_mock = pd.DataFrame(mock, index = indx)

### Cancellation 2 Layout ###
# delete 'app.' when ready to link to index page

count_fig = px.line(
    data_frame=df_mock,
    title = 'Cancellation Counts Over Time',
    labels = {
        'value': 'Cancellations',
        'index': 'Month',
        'variable': 'Reason',
    },
)

checklist = dbc.FormGroup(
    [
        dbc.Label("Choose Reasons (input options)"),
        dbc.Checklist(
            options=[
                {"label": "Too Many Meals", "value": 1},
                {"label": "Not Happy with Quality", "value": 2},
            ],
            value=[1],
            id="checklist-input",
        ),
    ]
)

month_slider = dcc.RangeSlider(
    id='month_slider',
    min=0,
    max=len(df_mock.index) - 1,
    step=None,
    marks={k:v for (k, v) in enumerate(df_mock.index)},
    value=[0, len(df_mock.index) - 1],
)

# Layout
app.layout = html.Div(
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
                )
            ],
            className = 'border mb-3 p-5',
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
            className = 'border mb-3',
        ),
    ]
)

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

### Development Server
# For isolated development purposes only, remove this section when ready
# to link to index
if __name__ == '__main__':
    app.run_server(debug=True)

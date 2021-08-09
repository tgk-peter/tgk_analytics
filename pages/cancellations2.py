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

# layout components
date_picker = dcc.DatePickerRange(
    id='date-picker-range',
    min_date_allowed=date(2019, 6, 1),
    max_date_allowed=date.today(),
    initial_visible_month=date.today(),
    start_date=pd.Timestamp('now').floor('D') - pd.Timedelta(7, unit="D"),
    end_date=pd.Timestamp('today').floor('D'),
)

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
                        date_picker,
                    ],
                )
            ],
            className = 'mb-3'
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dcc.Graph(figure=count_fig),
                    ],
                )
            ],
            className='border',
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        checklist,
                    ],
                )
            ],
        ),
    ]
)
'''
### Page 1 Callbacks ###
@app.callback(
    Output(
        component_id='page-1-content',
        component_property='children',
    ),
    [Input(
        component_id='page-1-dropdown',
        component_property='value',
    )]
)
def page_1_dropdown(value):
    return 'You have selected "{}"'.format(value)
'''
### Development Server
# For isolated development purposes only, remove this section when ready
# to link to index
if __name__ == '__main__':
    app.run_server(debug=True)

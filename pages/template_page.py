# Use as template for new pages #

# IMPORTS #
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from dotenv import load_dotenv
import os

# Import .env variables
load_dotenv()  # take environment variables from .env
CRP_PASSWORD = os.getenv('CRP_PASSWORD')

# Dash instance #
# For isolated development purposes only, remove this section when ready
# to link to index
external_stylesheets = [dbc.themes.UNITED]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Import Dash Instance #
# Uncomment when ready to link to index page
#from app import app

# PAGE LAYOUT #
# delete 'app.' when ready to link to index page
# change html.Container to html.Div

dropdown = dcc.Dropdown(
    id='page-1-dropdown',
    options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
    value='LA',
),

app.layout = dbc.Container(
    children=[
        dbc.Row(
            children=[
                dbc.Col(html.H1('Page 1')),
            ],
            className='',
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dropdown
                    ],
                ),
            ],
            className='border mb-3 py-3',
        ),
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

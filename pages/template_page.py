#### Use as template for new pages ####

### Import Packages ###
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

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

### Page 1 Layout ###
# delete 'app.' when ready to link to index page
app.layout = html.Div(
    children=[
        html.H1(
            children='Page 1',
        ),
        dcc.Dropdown(
            id='page-1-dropdown',
            options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
            value='LA',
        ),
        html.Div(
            id='page-1-content',
        ),
    ]
)

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

### Development Server
# For isolated development purposes only, remove this section when ready
# to link to index
if __name__ == '__main__':
    app.run_server(debug=True)

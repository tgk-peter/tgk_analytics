### Import Packages ###
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

### Import Dash Instance ###
#from app import app

### Dash instance ###
external_stylesheets = [dbc.themes.UNITED]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


### Page 2 Layout and Callbacks ###
app.layout = html.Div(
    children=[
        html.H1(
            children='Page 2',
        ),
        dcc.RadioItems(
            id='page-2-radios',
            options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
            value='Orange',
        ),
        html.Div(
            id='page-2-content',
        ),
        html.Br(),
        dcc.Link(
            children='Go to Page 1',
            href='/page-1',
        ),
        html.Br(),
        dcc.Link('Go back to home', href='/')
    ]
)

@app.callback(
    Output(
        component_id='page-2-content',
        component_property='children',
    ),
    [Input(
        component_id='page-2-radios',
        component_property='value',
    )]
)
def page_2_radios(value):
    return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)

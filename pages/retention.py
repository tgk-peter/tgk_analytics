#### Use as template for new pages ####

### Import Packages ###
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

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

### DataFrame ###
retain_dict = {
    'Cohort': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    'Customers': [500, 450, 475, 460],
    1: [.9, .6, .3, .1],
    2: [.8, .5, .2, 0],
    3: [.7, .4 , .1, 0],
    4: [.6, .3 , 0, 0],
}

df_retain = pd.DataFrame(retain_dict)



### Page 1 Layout ###
# delete 'app.' when ready to link to index page
week1 = go.Scatter(x=['Order 1','Order 2',' Order 3',' Order 4'], y=[.9, .6, .3, .1])
week2 = go.Scatter(x=['Order 1','Order 2',' Order 3',' Order 4'], y=[.8, .5, .2, 0])
week3 = go.Scatter(x=['Order 1','Order 2',' Order 3',' Order 4'], y=[.7, .4 , .1, 0])
week4 = go.Scatter(x=['Order 1','Order 2',' Order 3',' Order 4'], y=[.6, .3 , 0, 0])
data = [week1, week2, week3, week4]
layout={}
fig = go.Figure(data=data, layout=layout)


app.layout = html.Div(
    children=[
        dbc.Table.from_dataframe(df_retain, striped=True, bordered=True, hover=True),
        dcc.Graph(
            figure=fig
        ),
        dcc.Markdown('''
            ### Discussion ##
            - customers that only have one sub over lifetime vs several
            - how to break down weekly cohorts (Mon - Sun)?
        '''),
    ]
)

### Page 1 Callbacks ###
'''
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

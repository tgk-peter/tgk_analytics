# retention_order.py
# Generate order retention cohorts for TGK customers

### Import Packages ###
import cryptpandas as crp
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash_table import DataTable
from dash_table.Format import Format, Scheme
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

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
# Read in encrypted DataFrame
####REMOVE relative reference when deploy#######
df_orders_sub = crp.read_encrypted(path='../data_cache/active_order_cache.crypt', \
                password=CRP_PASSWORD)

# Groupby email and reset index. Aggregrate first order date and order count.
df_orders_group = df_orders_sub.groupby('email', as_index=False)
df_orders_agg = df_orders_group.agg(
                  first_order_date=('created_at','min'),
                  order_count=('order_number', 'count'),
                )
## create columns to track number of orders
for number in range(2,11):
  order_number = number
  df_orders_agg[f'{order_number} Order'] = df_orders_agg['order_count'] >= order_number

# function to create dictionary of order count column aggregrations
def df_retain_orders_columns():
  agg_dict = {'email':'count'}
  for column_name in df_orders_agg.columns[3:]:
    key = column_name
    value = 'sum'
    agg_dict[key] = value
  return agg_dict

# Resample into weeks to generate absolute counts
df_retain_orders = df_orders_agg.resample('W', on='first_order_date') \
                    .agg(df_retain_orders_columns())

# Divide by customers to generate percentages
df_retain_orders_percent = df_retain_orders.iloc[:, 1:] \
                            .div(df_retain_orders['email'], axis=0)

### Format
# Format for percentage table
df_retain_orders_percent_table = pd.concat([df_retain_orders['email'], df_retain_orders_percent], axis=1)
df_retain_orders_percent_table.reset_index(inplace=True)
df_retain_orders_percent_table['first_order_date'] = \
    df_retain_orders_percent_table['first_order_date'].dt.strftime('%Y-%m-%d')
df_retain_orders_percent_table.rename(
    columns={
        'email':'Customers',
        'first_order_date':'First Order Week'
    },
    inplace=True,
)

# Format for percentage graph
df_retain_graph = df_retain_orders_percent.transpose()

# Format for dbc.Table absolute
df_retain_orders.reset_index(inplace=True)
df_retain_orders['first_order_date'] = df_retain_orders['first_order_date'] \
                                        .dt.strftime('%Y-%m-%d')
df_retain_orders.rename(
    columns={
        'email':'Customers',
        'first_order_date':'First Order Week'
    },
    inplace=True,
)




####################
### Page Layout ####
####################

# layout components #
retention_trace = px.line(
    data_frame=df_retain_graph,
)

### DataTable ###

# Table columns
retention_table_percent_columns = \
    [{'name': i, 'id': i} for i in df_retain_orders_percent_table.columns[0:2]] + \
    [{'name': i, 'id': i, 'type':'numeric',
    'format':Format(precision=0, scheme=Scheme.percentage)} \
    for i in df_retain_orders_percent_table.columns[2:]]

# conditional styling
conditional_style_1 = [
    {
        'if': {
            'filter_query': '{{{col}}} >= .8 && {{{col}}} <= 1'.format(col=col),
            'column_id': col
        },
        'backgroundColor': '#045a8d',
        'color': 'white'
    } for col in df_retain_orders_percent_table.columns
]
conditional_style_2 = [
    {
        'if': {
            'filter_query': '{{{col}}} >= .6 && {{{col}}} <.8'.format(col=col),
            'column_id': col
        },
        'backgroundColor': '#2b8cbe',
        'color': 'white'
    } for col in df_retain_orders_percent_table.columns
]
conditional_style_3 = [
    {
        'if': {
            'filter_query': '{{{col}}} >= .4 && {{{col}}} <.6'.format(col=col),
            'column_id': col
        },
        'backgroundColor': '#74a9cf',
        'color': 'white'
    } for col in df_retain_orders_percent_table.columns
]
conditional_style_4 = [
    {
        'if': {
            'filter_query': '{{{col}}} >= .2 && {{{col}}} <.4'.format(col=col),
            'column_id': col
        },
        'backgroundColor': '#bdc9e1',
        'color': 'black'
    } for col in df_retain_orders_percent_table.columns
]
conditional_style_5 = [
    {
        'if': {
            'filter_query': '{{{col}}} >= .01 && {{{col}}} <.2'.format(col=col),
            'column_id': col
        },
        'backgroundColor': '#f1eef6',
        'color': 'black'
    } for col in df_retain_orders_percent_table.columns
]
conditional_style_all = conditional_style_1 + conditional_style_2 + \
    conditional_style_3 + conditional_style_4 + conditional_style_5

# Table setup
retention_table_percent = DataTable(
    id='retention_table_percent',
    columns=retention_table_percent_columns,
    data=df_retain_orders_percent_table.to_dict('records'),
    page_size=26,
    style_cell={'textAlign': 'center', 'fontSize':16, 'font-family':'Ubuntu'},
    filter_action='native',
    style_data_conditional= conditional_style_all,
)

### Layout ###
app.layout = dbc.Container(
    children=[
        dbc.Row(
            children=[
                dbc.Col(html.H1("Retention By Order Count")),
            ],
            className='mb-3',
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        #html.Div(legend, style={'float': 'right'}),
                        retention_table_percent,
                    ],
                ),
            ],
            className='mb-3',
        ),
        dcc.Graph(
            figure=retention_trace,
        ),
        dbc.Table.from_dataframe(df_retain_orders, striped=True, bordered=True, hover=True),
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

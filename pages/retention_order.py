# retention_order.py
# Generate order retention cohorts for TGK customers

### Import Packages ###
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
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
for number in range(1,11):
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
df_retain_orders.reset_index(inplace=True)
df_retain_orders['first_order_date'] = df_retain_orders['first_order_date'] \
                                        .dt.strftime('%b %d, %Y')
df_retain_orders.rename(
    columns={
        'email':'Customers',
        'first_order_date':'First Order Week'
    },
    inplace=True
)
# Divide by customers to generate percentages
df_retain_orders_percent = df_retain_orders.iloc[:, 2:] \
                            .div(df_retain_orders['Customers'], axis=0)



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
        dbc.Table.from_dataframe(df_retain_orders, striped=True, bordered=True, hover=True),
        dbc.Table.from_dataframe(df_retain_orders_percent),
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

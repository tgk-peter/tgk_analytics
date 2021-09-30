# IMPORTS #
# import dash
# Packages #
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Import Dash Instance and Pages #
# Import server so Procfile runs
from app import server
# Import Dash app
from app import app
# Import pages
from pages import meal_tag, cancellations, cancellations2, retention_order
from pages import price_exempt

# Navbar #
navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem(
                    children='Cancellations',
                    href='/cancellations',
                    external_link=True
                ),
                dbc.DropdownMenuItem(
                    children='Cancellations Over Time',
                    href='/cancellations-over-time',
                    external_link=True
                ),
            ],
            nav=True,
            in_navbar=True,
            label='Cancellation',
        ),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem(
                    children='Retention By Order',
                    href='/retention-by-order',
                    external_link=True
                ),
            ],
            nav=True,
            in_navbar=True,
            label='Retention',
        ),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem(
                    children='Meal Tagging',
                    href='/meal-tag',
                    external_link=True
                ),
                dbc.DropdownMenuItem(
                    children='Price Exempt Customers',
                    href='/price-exempt',
                    external_link=True
                ),
            ],
            nav=True,
            in_navbar=True,
            label='Other',
        ),
    ],
    brand='TGK Analytics',
    brand_href='/',
    brand_external_link=True,
    color='primary',
    dark=True,
    className='my-3',
)

# Page container #
page_container = dbc.Container(
    children=[
        # represents the URL bar, doesn't render anything
        dcc.Location(
            id='url',
            refresh=False,
        ),
        navbar,
        # content will be rendered in this element
        html.Div(id='page-content')
    ]
)

# Set app layout to page container #
app.layout = page_container

# Index Page Layout #
index_layout = dbc.Jumbotron(
    children=[
        html.H1(
            children='Welcome to TGK Analytics',
            className='display-4',
        ),
        html.Br(),
        dcc.Link(
            children='Go to Meal Tagging',
            href='/meal-tag',
        ),
        html.Br(),
        dcc.Link(
            children='Go to Cancellations',
            href='/cancellations',
        ),
        html.Br(),
        dcc.Link(
            children='Go to Cancellations over Time',
            href='/cancellations-over-time',
        ),
        html.Br(),
        dcc.Link(
            children='Go to Retention By Order',
            href='/retention-by-order',
        ),
        html.Br(),
        dcc.Link(
            children='Go to Price Increase Exempt Customers',
            href='/price-exempt',
        ),
    ]
)

# Assemble all layouts #
app.validation_layout = html.Div(
    children=[
        page_container,
        index_layout,
        meal_tag.layout,
        cancellations.layout,
        cancellations2.layout,
        retention_order.layout,
        price_exempt.layout
    ]
)

# Update Page Container #


@app.callback(
    Output(
        component_id='page-content',
        component_property='children',
        ),
    Input(
        component_id='url',
        component_property='pathname',
        )
)
def display_page(pathname):
    switcher = {
        '/': index_layout,
        '/meal-tag': meal_tag.layout,
        '/cancellations': cancellations.layout,
        '/cancellations-over-time': cancellations2.layout,
        '/retention-by-order': retention_order.layout,
        '/price-exempt': price_exempt.layout
    }
    return switcher.get(pathname, '404')

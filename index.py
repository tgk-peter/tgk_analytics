### Import Packages ###
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

### Import Dash Instance and Pages ###
from app import app
from pages import page_1, page_2, meal_tag, cancellations

### Page container ###
page_container = html.Div(
    children=[
        # represents the URL bar, doesn't render anything
        dcc.Location(
            id='url',
            refresh=False,
        ),
        # content will be rendered in this element
        html.Div(id='page-content')
    ]
)

### Set app layout to page container ###
app.layout = page_container

### Index Page Layout ###
index_layout = dbc.Jumbotron(
    children=[
        html.H1(
            children="Welcome to TGK Analytics",
            className="display-4",
        ),
        dcc.Link(
            children='Go to Page 1',
            href='/page-1',
        ),
        html.Br(),
        dcc.Link(
            children='Go to Page 2',
            href='/page-2',
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
    ]
)

### Assemble all layouts ###
app.validation_layout = html.Div(
    children = [
        page_container,
        index_layout,
        page_1.layout,
        page_2.layout,
        meal_tag.layout,
        cancellations.layout,
    ]
)

### Update Page Container ###
@app.callback(
    Output(
        component_id='page-content',
        component_property='children',
        ),
    [Input(
        component_id='url',
        component_property='pathname',
        )]
)
def display_page(pathname):
    switcher = {
        "/" : index_layout,
        "/page-1" : page_1.layout,
        "/page-2" : page_2.layout,
        "/meal-tag" : meal_tag.layout,
        "/cancellations" : cancellations.layout,
    }
    return switcher.get(pathname, "404")

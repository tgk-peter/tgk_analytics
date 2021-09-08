# Import Packages #
import dash
import dash_auth
import dash_bootstrap_components as dbc

# Import .env variables #
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
dash_username = os.getenv('DASH_USERNAME')
dash_password = os.getenv('DASH_PASSWORD')
VALID_USERNAME_PASSWORD_PAIRS = {dash_username: dash_password}

# Dash instance #
external_stylesheets = [dbc.themes.UNITED]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS,
)
server = app.server

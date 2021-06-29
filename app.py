### Import Packages ###
import dash
import dash_auth
import dash_bootstrap_components as dbc

# REMOVE AT DEPLOYMENT
VALID_USERNAME_PASSWORD_PAIRS = {
    'hello': 'world'
}

### Dash instance ###
external_stylesheets = [dbc.themes.UNITED]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS,
)
# Uncomment at deployment 
#server = app.server

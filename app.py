### Import Packages ###
import dash
import dash_bootstrap_components as dbc

### Dash instance ###
external_stylesheets = [dbc.themes.UNITED]
app = dash.Dash(
        __name__,
        external_stylesheets=external_stylesheets,
        )

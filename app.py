import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from callbacks import register_callbacks


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.config.suppress_callback_exceptions = True
server = app.server

app.layout = html.Div([
        dcc.Store(id="data-store", storage_type="local"),
        dcc.Store(id="current-user", storage_type="local"),
        dcc.Location(id="url"),

        html.Div(id="header-bar"),  # будет обновляться в коллбэке

        html.Div(id="page-content"),
        dcc.Dropdown(id="test-group", style={"display": "none"})
    ])

# Коллбэки
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)

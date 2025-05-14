from dash import Dash
from layout import create_layout
from callbacks import register_callbacks
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True  # позволяет использовать динамические компоненты
)

app.title = "SNTK Dashboard"
app.layout = create_layout()

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)

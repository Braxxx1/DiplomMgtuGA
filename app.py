import dash
import dash_bootstrap_components as dbc
from dash import Output, Input
from layout.main_layout import create_layout
from callbacks import register_callbacks
from pages import register 
# Импорт страниц
from pages import dashboard, preprocessing

# Инициализация Dash
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server = app.server  # для деплоя, если понадобится

# Основный layout — Navbar + router
app.layout = create_layout()

# Роутинг по url
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page(pathname):
    if pathname == "/preprocessing":
        return preprocessing.layout
    elif pathname == "/register":
        return register.layout
    return dashboard.layout

# Регистрируем все коллбэки
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate
from callbacks import register_callbacks
from layout.main_layout import create_layout
from pages import dashboard, preprocessing, register, login

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.config.suppress_callback_exceptions = True
server = app.server

# app.layout = create_layout()
app.layout = html.Div([
        dcc.Store(id="data-store", storage_type="local"),
        dcc.Store(id="current-user", storage_type="local"),
        dcc.Location(id="url"),

        html.Div(id="header-bar"),  # будет обновляться в коллбэке

        html.Div(id="page-content")
    ])

@app.callback(
    Output("page-content", "children"),
    Output("url", "pathname", allow_duplicate=True),
    Input("url", "pathname"),
    Input("current-user", "data"),
    prevent_initial_call="initial_duplicate"
)
def route_pages(path, user):
    protected = ["/dashboard", "/preprocessing"]
    print(user, path)
    # Нельзя пускать на защищенные страницы без авторизации
    if path in protected and not user:
        if path != "/login":
            return login.layout, "/login"
        return login.layout, no_update

    if path == "/dashboard":
        return dashboard.layout, path
    elif path == "/preprocessing":
        return preprocessing.layout, path
    elif path == "/register":
        return register.layout, path
    elif path == "/login":
        return login.layout, no_update

    # fallback
    if not user:
        if path != "/login":
            return login.layout, "/login"
        return login.layout, no_update
    return dashboard.layout, "/dashboard"  # например, дефолт для авторизованных


# 👤 Обновление шапки с именем и кнопкой выхода
@app.callback(
    Output("header-bar", "children"),
    Input("current-user", "data")
)
def update_header(user):
    print("🧠 Header user =", user)
    if not user:
        return ""

    name = user.get("name", "")
    role = user.get("role", "")
    role_name = "Преподаватель" if role == "teacher" else "Студент"

    return dbc.NavbarSimple([
        dbc.NavItem(html.Span(f"👤 {role_name} {name}", className="me-3 text-white")),
        dbc.NavItem(dcc.Link("📊 Аналитика", href="/dashboard", className="nav-link")),
        dbc.NavItem(dcc.Link("⚙️ Предобработка", href="/preprocessing", className="nav-link")),
        dbc.Button("Выйти", id="logout-btn", color="light", size="sm", className="ms-3")
    ], brand="Data Dashboard", color="primary", dark=True, className="mb-4")

@app.callback(
    Output("current-user", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("logout-btn", "n_clicks"),
    State("current-user", "data"),
    prevent_initial_call=True
)
def logout(n_clicks, user):
    if not n_clicks or not user:
        raise PreventUpdate
    return None, "/login"



# Коллбэки
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)

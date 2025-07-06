# pages/register.py
import dash_bootstrap_components as dbc
from dash import dcc, html

layout = html.Div(
    dbc.Container([
        html.Div([
            html.H3("🎓 Регистрация студента", className="text-center mb-4"),

            dbc.Label("Имя"),
            dbc.Input(id="reg-name", placeholder="Иван Иванов", className="mb-3"),

            dbc.Label("Email"),
            dbc.Input(id="reg-email", type="email", placeholder="you@example.com", className="mb-3"),

            dbc.Label("Пароль"),
            dbc.Input(id="reg-password", type="password", placeholder="••••••••", className="mb-3"),

            dbc.Label("Группа"),
            dcc.Dropdown(id="reg-group", placeholder="Выберите группу", className="mb-3"),

            dbc.Button("Зарегистрироваться", id="reg-submit", color="success", className="w-100 mt-2"),
            html.Div(id="reg-message", className="mt-3 text-center"),

            html.Div([
                html.Span("Уже есть аккаунт? "),
                dcc.Link("Войти", href="/login")
            ], className="mt-3 text-center")

        ], className="p-4 rounded shadow bg-white", style={"width": "100%", "maxWidth": "400px"})
    ], className="d-flex justify-content-center align-items-center", style={"height": "100vh"})
)

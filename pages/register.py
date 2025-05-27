from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.H3("📝 Регистрация пользователя", className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Имя:"),
            dbc.Input(id="reg-name", type="text", placeholder="Иван Иванов", className="mb-3"),

            dbc.Label("Email:"),
            dbc.Input(id="reg-email", type="email", placeholder="you@example.com", className="mb-3"),

            dbc.Label("Пароль:"),
            dbc.Input(id="reg-password", type="password", placeholder="••••••••", className="mb-3"),

            dbc.Label("Роль:"),
            dcc.Dropdown(
                id="reg-role",
                options=[
                    {"label": "Студент", "value": "student"},
                    {"label": "Преподаватель", "value": "teacher"}
                ],
                placeholder="Выберите роль",
                className="mb-4"
            ),

            html.Button("✅ Зарегистрироваться", id="reg-submit", className="btn btn-success"),
            html.Div(id="reg-message", className="mt-3")
        ], width=6)
    ])
], fluid=True)

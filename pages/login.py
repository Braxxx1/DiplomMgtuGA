from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([

                    html.H3("Вход в систему", className="text-center mb-4"),

                    dbc.Input(id="login-email", type="email", placeholder="Email", className="mb-3"),
                    dbc.Input(id="login-password", type="password", placeholder="Пароль", className="mb-3"),

                    dbc.Button("Войти", id="login-submit", color="primary", className="w-100"),

                    html.Div(id="login-message", className="mt-3 text-danger text-center"),

                    html.Div(
                        dcc.Link("Нет аккаунта? Зарегистрироваться", href="/register"),
                        className="text-center mt-4"
                    ),

                    # dcc.Store(id="current-user", storage_type="session"),
                    # dcc.Location(id="login-redirect")
                ]),
                className="p-4 shadow rounded",
                style={"maxWidth": "400px", "margin": "0 auto"}
            ),
            width=12,
            className="d-flex justify-content-center align-items-start",
            style={"height": "100vh", "paddingTop": "10vh"}  # поднято выше центра
        )
    ),
    fluid=True
)

# pages/profile.py
from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.H2("👤 Профиль пользователя", className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.Div(id="profile-info")
        ], width=6)
    ])
], fluid=True)

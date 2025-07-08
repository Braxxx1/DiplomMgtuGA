# pages/test.py
import dash_bootstrap_components as dbc
from dash import dcc, html

layout = dbc.Container([
    # dcc.Location(id="url"),
    dcc.Store(id="selected-test-id"),
    dcc.Store(id="test-questions-store"),
    dcc.Store(id="current-question-index", data=0),
    dcc.Store(id="answers-store", data={}),
    

    dbc.Row([
        dbc.Col([
            html.H3("📄 Прохождение теста", className="text-center mb-4"),

            html.Div(id="test-question-form", className="mb-4"),

            html.Div([
                dbc.Button("← Назад", id="prev-question-btn", color="secondary", className="me-2", style={"display": "none"}),
                dbc.Button("Далее →", id="next-question-btn", color="primary", style={"display": "none"}),
                dbc.Button("✅ Завершить", id="submit-test-btn", color="success", style={"display": "none"})
            ], className="d-flex justify-content-center", id="test-nav-buttons"),

            html.Div(id="test-submit-msg", className="mt-4 text-center")
        ], width=8)
    ], justify="center")
], fluid=True)

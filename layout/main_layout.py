# import dash_bootstrap_components as dbc
# from dash import dcc, html


# def create_layout():
#     return html.Div([
#         dcc.Store(id="data-store", storage_type="local"),
#         dcc.Location(id="url"),

#         dbc.NavbarSimple(
#             children=[
#                 dbc.NavItem(dcc.Link("📊 Аналитика", href="/dashboard", className="nav-link")),
#                 dbc.NavItem(dcc.Link("⚙️ Предобработка", href="/preprocessing", className="nav-link")),
#             ],
#             brand="Data Dashboard",
#             brand_href="/dashboard",
#             color="primary",
#             dark=True,
#             className="mb-4"
#         ),

#         html.Div(id="page-content")
#     ])
# main_layout.py
import dash_bootstrap_components as dbc
from dash import dcc, html

def create_layout():
    return html.Div([
        dcc.Store(id="data-store", storage_type="local"),
        dcc.Store(id="current-user", storage_type="session"),
        dcc.Location(id="url"),

        html.Div(id="header-bar"),  # будет обновляться в коллбэке

        html.Div(id="page-content")
    ])

import dash_bootstrap_components as dbc
from dash import dcc, html

layout = dbc.Container([
    dcc.Store(id="data-store", storage_type="local"),
    dcc.Store(id="data-store-processed", storage_type="local"),

    dcc.Download(id="corr-download"),

    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id="upload-data",
                children=html.Div(["Перетащите CSV-файл или ", html.A("выберите")]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "marginBottom": "20px"
                },
                multiple=False
            ),
            html.Div(id="upload-status"),
            html.Div(id="data-preview")
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Выберите столбец для анализа:"),
            dcc.Dropdown(id="column-dropdown", className="mb-3"),

            dcc.Tabs(id="tabs", value="distribution", children=[
                dcc.Tab(label="Распределение", value="distribution", children=[
                    html.Div([dcc.RadioItems(id="plot-type", style={"display": "none"})], id="plot-type-container"),
                    html.Div(id="scatter-y-dropdown-container"),
                    dcc.Dropdown(id="scatter-y-column", style={"display": "none"})
                ]),
                dcc.Tab(label="Выбросы (Boxplot)", value="outliers"),
                dcc.Tab(label="Корреляция", value="correlation", children=[
                    html.Div([
                        html.Label("Порог корреляции (|значение| >):"),
                        dcc.Slider(
                            id="corr-threshold",
                            min=0,
                            max=1,
                            step=0.05,
                            value=0.0,
                            marks={0: '0', 0.5: '0.5', 1: '1.0'}
                        ),
                        html.Button("📥 Скачать CSV", id="download-btn", className="mt-2")
                    ], className="p-3")
                ]),
                dcc.Tab(label="Пропуски", value="missing"),
                dcc.Tab(label="Дубликаты", value="duplicates")
            ])
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Аналитика"),
                dbc.CardBody([html.Div(id="graph-container")])
            ]),
            dbc.Card([
                dbc.CardHeader("Статистика"),
                dbc.CardBody([html.Div(id="summary-container")])
            ], className="mt-3")
        ], width=6)
    ])
], fluid=True)

import dash_bootstrap_components as dbc
from dash import dcc, html

layout = dbc.Container([
    dcc.Store(id="data-store", storage_type="local"),

    dcc.Download(id="processed-download"),

    html.Div([
        html.H5("📋 Предпросмотр данных:", className="mb-2"),
        html.Div(id="processing-preview")
    ], className="mb-4"),

    html.H4("⚙️ Инструменты предобработки", className="mb-4"),

    dbc.Row([
        dbc.Col([  # Сайдбар
            dbc.ListGroup([
                dbc.ListGroupItem("🗑 Удаление колонок", id="tab-remove", action=True, active=True),
                dbc.ListGroupItem("🧼 Обработка NaN", id="tab-nan", action=True),
                dbc.ListGroupItem("🔀 Преобразование типов", id="tab-types", action=True),
                dbc.ListGroupItem("✏️ Переименование", id="tab-rename", action=True),
                dbc.ListGroupItem("🔄 Замена значений", id="tab-replace", action=True),
                dbc.ListGroupItem("🧹 Удаление дубликатов", id="tab-duplicates", action=True),
                dbc.ListGroupItem("🧮 Удаление по условию", id="tab-condition", action=True),
                dbc.ListGroupItem("🏷 Label Encoder", id="tab-categorical", action=True),
            ], id="prep-tabs")
        ], width=3),

        dbc.Col([  # Контент выбранной вкладки
            html.Div(id="prep-content")
        ], width=9)
    ], className="gx-5"),

    html.Div([
        html.Button("📥 Скачать", id="download-processed", className="btn btn-secondary mt-4")
    ])
], fluid=True)

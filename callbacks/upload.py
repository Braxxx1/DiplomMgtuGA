# callbacks/upload.py
import base64
import io

import pandas as pd
from dash import Input, Output, State, dash_table, html, no_update


def register_upload_callbacks(app):
    # 1. Загрузка и сохранение в Store
    @app.callback(
        Output("data-store", "data"),
        Output("data-store-processed", "data"),
        Output("upload-status", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename")
    )
    def load_csv(contents, filename):
        if contents is None:
            return no_update, no_update, ""
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            return df.to_dict("records"), df.to_dict("records"), f"✅ Загружен файл: {filename} ({df.shape[0]} строк и {df.shape[1]} столбцов)"
        except Exception as e:
            return None, None, f"❌ Ошибка при загрузке: {e}"


    # 2. Превью первых строк таблицы
    @app.callback(
        Output("data-preview", "children"),
        Input("data-store", "data")
    )
    def show_data_preview(data):
        if data is None:
            return ""
        df = pd.DataFrame(data).head(5)
        return dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
            page_action="none",
            style_header={"fontWeight": "bold"}
        )

    # 3. Обновление дропдауна выбора колонки
    @app.callback(
        Output("column-dropdown", "options"),
        Output("column-dropdown", "value"),
        Input("data-store", "modified_timestamp"),
        State("data-store", "data")
    )
    def update_column_dropdown(ts, data):
        if not data:
            return no_update, no_update
        df = pd.DataFrame(data)
        options = [
            {"label": f"{col} {'🔢' if pd.api.types.is_numeric_dtype(df[col]) else '🔤'}", "value": col}
            for col in df.columns
        ]
        return options, df.columns[0]

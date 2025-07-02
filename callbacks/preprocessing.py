# callbacks/preprocessing.py
import dash_bootstrap_components as dbc
import pandas as pd
from dash import (Input, Output, State, callback_context, ctx, dash_table, dcc,
                  html, no_update)
from dash.dcc import send_data_frame
from dash.exceptions import PreventUpdate


def register_preprocessing_callbacks(app):
    # 3. Выгрузка обработанного файла
    @app.callback(
        Output("processed-download", "data"),
        Input("download-processed", "n_clicks"),
        State("data-store", "data"),
        prevent_initial_call=True
    )
    def download_processed(_, data):
        if not data:
            return no_update
        df = pd.DataFrame(data)
        return send_data_frame(df.to_csv, filename="processed_data.csv", index=False)


        # Предпросмотр обновлённого датафрейма
    
    
    @app.callback(
        Output("processing-preview", "children"),
        Input("data-store", "data")
    )
    def show_processing_preview(data):
        if not data:
            return html.Div("Нет данных для отображения.")
        df = pd.DataFrame(data).head(5)
        return dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": col, "id": col} for col in df.columns],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
            page_action="none",
            style_header={"fontWeight": "bold"}
        )
        
        
    @app.callback(
        Output("prep-content", "children"),
        Output("tab-remove", "active"),
        Output("tab-nan", "active"),
        Output("tab-types", "active"),
        Output("tab-rename", "active"),
        Output("tab-replace", "active"),
        Output("tab-duplicates", "active"),
        Output("tab-condition", "active"),
        Output("tab-categorical", "active"),
        Input("tab-remove", "n_clicks"),
        Input("tab-nan", "n_clicks"),
        Input("tab-types", "n_clicks"),
        Input("tab-rename", "n_clicks"),
        Input("tab-replace", "n_clicks"),
        Input("tab-duplicates", "n_clicks"),
        Input("tab-condition", "n_clicks"),
        Input("tab-categorical", "n_clicks"),
        prevent_initial_call=True
    )
    def display_prep_tab(_, __, ___, ____, _____, ______, _______, ________):
        tab_id = ctx.triggered_id or "tab-remove"

        remove = tab_id == "tab-remove"
        nan = tab_id == "tab-nan"
        types = tab_id == "tab-types"
        rename = tab_id == "tab-rename"
        replace = tab_id == "tab-replace"
        duplicates = tab_id == "tab-duplicates"
        condition = tab_id == "tab-condition"
        categorical = tab_id == "tab-categorical"

        
        if remove:
            content = html.Div([
                html.H5("🗑 Удаление колонок"),
                html.Label("Выберите столбцы для удаления:"),
                dcc.Dropdown(id="drop-columns", multi=True),
                html.Button("💾 Применить удаление", id="apply-remove", className="btn btn-primary mt-3")
            ])
        elif nan:
            content = html.Div([
                html.H5("🧼 Обработка пропусков"),
                html.Label("Выберите столбцы для обработки NaN:", className="mb-1"),
                dcc.Dropdown(id="nan-columns", multi=True, className="mb-3"),

                html.Label("Стратегия обработки:", className="mb-1"),
                dcc.RadioItems(
                    id="fillna-strategy",
                    options=[
                        {"label": "Среднее (числовые)", "value": "mean"},
                        {"label": "Медиана (числовые)", "value": "median"},
                        {"label": "Заполнить 0", "value": "zero"},
                        {"label": "Пустая строка", "value": "empty"},
                        {"label": "Удалить строки с NaN", "value": "drop"}
                    ],
                    labelStyle={"display": "block", "marginBottom": "6px"},
                    inputStyle={"marginRight": "8px"}
                ),
                html.Button("💾 Применить заполнение", id="apply-nan", className="btn btn-primary mt-3")
            ])
        elif types:
            content = html.Div([
                html.H5("🔀 Преобразование типов"),
                html.Label("Столбец для преобразования:"),
                dcc.Dropdown(id="type-column"),
                html.Label("Целевой тип:"),
                dcc.Dropdown(
                    id="type-target",
                    options=[
                        {"label": "str", "value": "str"},
                        {"label": "int", "value": "int"},
                        {"label": "float", "value": "float"}
                    ]
                ),
                html.Button("💾 Применить преобразование", id="apply-type", className="btn btn-primary mt-3")
            ])
        elif rename:
            content = html.Div([
                html.H5("✏️ Переименование столбца"),
                html.Label("Столбец для переименования:"),
                dcc.Dropdown(id="rename-column"),
                html.Label("Новое имя:"),
                dbc.Input(id="rename-new-name", type="text", placeholder="Введите новое имя"),
                html.Button("💾 Переименовать", id="apply-rename", className="btn btn-primary mt-3")
            ])
        elif replace:
            content = html.Div([
                html.H5("🔄 Замена значений в столбце"),
                html.Label("Столбец:"),
                dcc.Dropdown(id="replace-column", className="mb-2"),
                html.Label("Что заменить:"),
                dbc.Input(id="replace-from", placeholder="Старое значение", type="text", className="mb-2"),
                html.Label("На что заменить:"),
                dbc.Input(id="replace-to", placeholder="Новое значение", type="text", className="mb-2"),
                html.Button("💾 Заменить", id="apply-replace", className="btn btn-primary mt-2")
            ])
        elif duplicates:
            content = html.Div([
                html.H5("🧹 Удаление дубликатов"),
                html.Label("Удалить дубликаты по столбцам (оставить пустым — все):"),
                dcc.Dropdown(id="dup-columns", multi=True, className="mb-3"),
                html.Button("🗑 Удалить дубликаты", id="apply-duplicates", className="btn btn-danger")
            ])
        elif condition:
            content = html.Div([
                html.H5("🧮 Удаление строк по условию"),
                html.Label("Столбец:"),
                dcc.Dropdown(id="cond-column", className="mb-2"),

                html.Label("Оператор:"),
                dcc.Dropdown(
                    id="cond-operator",
                    options=[
                        {"label": "== равно", "value": "=="},
                        {"label": "!= не равно", "value": "!="},
                        {"label": "> больше", "value": ">"},
                        {"label": "< меньше", "value": "<"},
                        {"label": "содержит (текст)", "value": "contains"}
                    ],
                    className="mb-2"
                ),

                html.Label("Значение:"),
                dbc.Input(id="cond-value", type="text", className="mb-3"),
                html.Div(id="cond-preview", className="mb-2 text-muted"),

                html.Button("🗑 Удалить строки", id="apply-condition", className="btn btn-danger")
            ])
        elif categorical:
            content = html.Div([
                html.H5("🏷 Label Encoding (числовые коды)"),
                html.Label("Выберите столбец:"),
                dcc.Dropdown(id="cat-column", className="mb-3"),
                html.Button("🔢 Закодировать", id="apply-categorical", className="btn btn-primary mt-2")
            ])


        else:
            content = html.Div("Выберите действие слева")

        return content, remove, nan, types, rename, replace, duplicates, condition, categorical


    @app.callback(
        Output("drop-columns", "options"),
        Input("data-store", "data")
    )
    def update_drop_options(data):
        if not data:
            return []
        df = pd.DataFrame(data)
        return [{"label": col, "value": col} for col in df.columns]


    @app.callback(
        Output("nan-columns", "options"),
        Input("data-store", "data"),
        Input("tab-nan", "n_clicks"),
    )
    def update_nan_options(data, _):
        if not data:
            raise PreventUpdate
        df = pd.DataFrame(data)
        return [{"label": col, "value": col} for col in df.columns]


    @app.callback(
    Output("type-column", "options"),
    Input("data-store", "data"),
    Input("tab-types", "n_clicks"),
    )
    def update_type_column_options(data, _):
        if not data:
            raise PreventUpdate
        df = pd.DataFrame(data)
        return [{"label": col, "value": col} for col in df.columns]


    @app.callback(
    Output("rename-column", "options"),
    Input("data-store", "data"),
    Input("tab-rename", "n_clicks"),
    )
    def update_rename_column_options(data, _):
        if not data:
            raise PreventUpdate
        df = pd.DataFrame(data)
        return [{"label": col, "value": col} for col in df.columns]

    
    @app.callback(
        Output("data-store", "data", allow_duplicate=True),
        Input("apply-remove", "n_clicks"),
        State("data-store", "data"),
        State("drop-columns", "value"),
        prevent_initial_call=True
    )
    def apply_column_removal(_, data, cols_to_remove):
        if not data or not cols_to_remove:
            raise PreventUpdate
        df = pd.DataFrame(data)
        df.drop(columns=cols_to_remove, inplace=True, errors="ignore")
        return df.to_dict("records")


    @app.callback(
        Output("data-store", "data", allow_duplicate=True),
        Input("apply-nan", "n_clicks"),
        State("data-store", "data"),
        State("nan-columns", "value"),
        State("fillna-strategy", "value"),
        prevent_initial_call=True
    )
    def apply_fillna(_, data, columns, strategy):
        if not data or not columns or not strategy:
            raise PreventUpdate
        df = pd.DataFrame(data)

        if strategy == "mean":
            for col in columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].mean())
        elif strategy == "median":
            for col in columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
        elif strategy == "zero":
            df[columns] = df[columns].fillna(0)
        elif strategy == "empty":
            df[columns] = df[columns].fillna("")
        elif strategy == "drop":
            df.dropna(subset=columns, inplace=True)

        return df.to_dict("records")


    @app.callback(
        Output("data-store", "data", allow_duplicate=True),
        Input("apply-type", "n_clicks"),
        State("data-store", "data"),
        State("type-column", "value"),
        State("type-target", "value"),
        prevent_initial_call=True
    )
    def apply_type_cast(_, data, col, target_type):
        if not data or not col or not target_type:
            raise PreventUpdate
        df = pd.DataFrame(data)
        try:
            df[col] = df[col].astype(target_type)
        except Exception:
            raise PreventUpdate
        return df.to_dict("records")


    @app.callback(
        Output("data-store", "data", allow_duplicate=True),
        Input("apply-rename", "n_clicks"),
        State("data-store", "data"),
        State("rename-column", "value"),
        State("rename-new-name", "value"),
        prevent_initial_call=True
    )
    def apply_rename_column(_, data, old_col, new_col):
        if not data or not old_col or not new_col:
            raise PreventUpdate
        df = pd.DataFrame(data)
        if old_col not in df.columns or new_col.strip() == "":
            raise PreventUpdate
        df.rename(columns={old_col: new_col.strip()}, inplace=True)
        return df.to_dict("records")


    @app.callback(
        Output("replace-column", "options"),
        Input("data-store", "data"),
        Input("tab-replace", "n_clicks"),
    )
    def update_replace_column(data, _):
        if not data:
            raise PreventUpdate
        df = pd.DataFrame(data)
        return [{"label": col, "value": col} for col in df.columns]


    @app.callback(
        Output("data-store", "data", allow_duplicate=True),
        Input("apply-replace", "n_clicks"),
        State("data-store", "data"),
        State("replace-column", "value"),
        State("replace-from", "value"),
        State("replace-to", "value"),
        prevent_initial_call=True
    )
    def apply_value_replace(_, data, col, old_val, new_val):
        if not data or not col or old_val is None or new_val is None:
            raise PreventUpdate
        df = pd.DataFrame(data)
        df[col] = df[col].replace(old_val, new_val)
        return df.to_dict("records")


    @app.callback(
        Output("dup-columns", "options"),
        Input("data-store", "data"),
        Input("tab-duplicates", "n_clicks"),
    )
    def update_dup_column_options(data, _):
        if not data:
            raise PreventUpdate
        df = pd.DataFrame(data)
        return [{"label": col, "value": col} for col in df.columns]


    @app.callback(
        Output("data-store", "data", allow_duplicate=True),
        Input("apply-duplicates", "n_clicks"),
        State("data-store", "data"),
        State("dup-columns", "value"),
        prevent_initial_call=True
    )
    def apply_duplicates_removal(_, data, subset_cols):
        if not data:
            raise PreventUpdate
        df = pd.DataFrame(data)
        df = df.drop_duplicates(subset=subset_cols if subset_cols else None)
        return df.to_dict("records")


    @app.callback(
        Output("cond-column", "options"),
        Input("data-store", "data"),
        Input("tab-condition", "n_clicks"),
    )
    def update_condition_column_options(data, _):
        if not data:
            raise PreventUpdate
        df = pd.DataFrame(data)
        return [{"label": col, "value": col} for col in df.columns]


    @app.callback(
    Output("data-store", "data", allow_duplicate=True),
    Input("apply-condition", "n_clicks"),
    State("data-store", "data"),
    State("cond-column", "value"),
    State("cond-operator", "value"),
    State("cond-value", "value"),
    prevent_initial_call=True
    )
    def apply_condition(_, data, column, operator, value):
        if not data or not column or not operator or value is None:
            raise PreventUpdate
        df = pd.DataFrame(data)

        try:
            if operator == "==":
                df = df[df[column] != value]
            elif operator == "!=":
                df = df[df[column] == value]
            elif operator == ">":
                df = df[~(pd.to_numeric(df[column], errors="coerce") > float(value))]
            elif operator == "<":
                df = df[~(pd.to_numeric(df[column], errors="coerce") < float(value))]
            elif operator == "contains":
                df = df[~df[column].astype(str).str.contains(value, na=False, case=False)]
        except Exception:
            raise PreventUpdate

        return df.to_dict("records")


    @app.callback(
        Output("cond-preview", "children"),
        Input("cond-column", "value"),
        Input("cond-operator", "value"),
        Input("cond-value", "value"),
        State("data-store", "data"),
        prevent_initial_call=True
    )
    def preview_condition(col, op, val, data):
        if not data or not col or not op or val is None:
            return ""

        df = pd.DataFrame(data)
        try:
            if op == "==":
                to_drop = df[df[col] == val]
            elif op == "!=":
                to_drop = df[df[col] != val]
            elif op == ">":
                to_drop = df[pd.to_numeric(df[col], errors="coerce") > float(val)]
            elif op == "<":
                to_drop = df[pd.to_numeric(df[col], errors="coerce") < float(val)]
            elif op == "contains":
                to_drop = df[df[col].astype(str).str.contains(val, na=False, case=False)]
            else:
                return ""
        except Exception:
            return html.Span("⚠️ Ошибка при попытке фильтрации", style={"color": "darkred"})

        return f"🔍 Будет удалено строк: {len(to_drop)}"


    @app.callback(
        Output("cat-column", "options"),
        Input("data-store", "data"),
        Input("tab-categorical", "n_clicks"),
    )
    def update_cat_column_options(data, _):
        if not data:
            raise PreventUpdate
        df = pd.DataFrame(data)
        return [{"label": col, "value": col} for col in df.columns]


    @app.callback(
        Output("data-store", "data", allow_duplicate=True),
        Input("apply-categorical", "n_clicks"),
        State("data-store", "data"),
        State("cat-column", "value"),
        prevent_initial_call=True
    )
    def apply_label_encoding(_, data, col):
        if not data or not col:
            raise PreventUpdate
        df = pd.DataFrame(data)
        try:
            df[col], _ = pd.factorize(df[col])
        except Exception:
            raise PreventUpdate
        return df.to_dict("records")

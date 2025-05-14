from dash import Input, Output, State, dcc, html, no_update, dash_table, ctx, Dash
from dash.dependencies import ClientsideFunction
from dash.dcc import send_data_frame
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import io
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np


def register_callbacks(app):
    # 1. Обработка загрузки файла
    @app.callback(
        Output("data-store", "data"),
        Output("upload-status", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename")
    )
    def load_csv(contents, filename):
        if contents is None:
            return no_update, ""
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            return df.to_dict("records"), f"✅ Загружен файл: {filename} ({df.shape[0]} строк и {df.shape[1]} столбцов)"
        except Exception as e:
            return None, f"❌ Ошибка при загрузке: {e}"

    # 2. Обновление списка колонок (в том числе при перезагрузке страницы)
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

    # 3. Превью данных
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

    # 3. Вкладка распределения → выбор типа графика
    @app.callback(
        Output("plot-type-container", "children"),
        Input("tabs", "value"),
        Input("column-dropdown", "value"),
        State("data-store", "data")
    )
    def show_plot_selector(tab, column, data):
        if tab != "distribution" or data is None or column is None:
            return None

        df = pd.DataFrame(data)
        is_numeric = pd.api.types.is_numeric_dtype(df[column])

        # Формируем доступные графики
        options = [{"label": "📊 Гистограмма", "value": "histogram"}]
        if is_numeric:
            options += [
                {"label": "🔵 KDE-график", "value": "density"},
                {"label": "🎻 Violin-график", "value": "violin"},
                {"label": "⚫ Scatter-график", "value": "scatter"},
            ]

        return html.Div([
            html.Label("Выберите тип графика:", className="mb-2 fw-bold"),
            dcc.RadioItems(
                id="plot-type",
                options=options,
                value="histogram",  # всегда допустим
                labelStyle={"display": "block", "margin-bottom": "8px"},
                inputStyle={"margin-right": "8px"},
                className="mb-3"
            )
        ], style={
            "backgroundColor": "#f8f9fa",
            "padding": "12px",
            "borderRadius": "8px",
            "border": "1px solid #dee2e6",
            "marginBottom": "10px"
        })

    # 4. Показать выбор Y-оси при scatter
    @app.callback(
        Output("scatter-y-dropdown-container", "children"),
        Input("plot-type", "value"),
        State("column-dropdown", "value"),
        State("data-store", "data")
    )
    def show_scatter_dropdown(plot_type, x_col, data):
        if plot_type != "scatter" or data is None:
            return None
        df = pd.DataFrame(data)
        numeric_columns = df.select_dtypes("number").columns
        options = [{"label": col, "value": col} for col in numeric_columns if col != x_col]
        if not options:
            return None
        return html.Div([
            html.Label("Сравнивать с:", className="fw-bold mb-1"),
            dcc.Dropdown(
                id="scatter-y-column",
                options=options,
                value=options[0]["value"],
                clearable=False,
                className="mb-3"
            )
        ])

    # 5. Отображение графика и статистики
    @app.callback(
        Output("graph-container", "children"),
        Output("summary-container", "children"),
        Input("column-dropdown", "value"),
        Input("tabs", "value"),
        Input("plot-type", "value"),
        Input("scatter-y-column", "value"),
        Input("corr-threshold", "value"),
        State("data-store", "data"),
        prevent_initial_call=True
    )
    def update_graph(column, tab, plot_type, scatter_y, threshold, data):
        if not column or data is None:
            return no_update, no_update
        df = pd.DataFrame(data)

        if tab == "distribution":
            if plot_type == "histogram":
                fig = px.histogram(df, x=column, nbins=30, title=f"Гистограмма: {column}")
            elif plot_type == "density":
                if pd.api.types.is_numeric_dtype(df[column]):
                    fig = px.density_contour(df, x=column, title=f"KDE-график: {column}")
                else:
                    fig = px.histogram(df, x=column, title=f"Гистограмма по частоте: {column}")
            elif plot_type == "violin":
                if pd.api.types.is_numeric_dtype(df[column]):
                    fig = px.violin(df, y=column, box=True, points="all", title=f"Violin-график: {column}")
                else:
                    fig = {}
            elif plot_type == "scatter":
                if scatter_y and all(pd.api.types.is_numeric_dtype(df[col]) for col in [column, scatter_y]):
                    fig = px.scatter(df, x=column, y=scatter_y, title=f"Scatter: {column} vs {scatter_y}")
                else:
                    fig = {}
            else:
                fig = {}
        elif tab == "outliers":
            if pd.api.types.is_numeric_dtype(df[column]):
                fig = px.box(df, x=column, points="outliers", title=f"Boxplot: {column}")
            else:
                fig = None  # триггерим текстовое предупреждение
        elif tab == "correlation":
            corr = df.select_dtypes("number").corr().round(2)

            if threshold > 0:
                # Обнуляем диагональ временно
                np.fill_diagonal(corr.values, 0)

                # Маска по порогу
                mask = corr.abs() >= threshold
                keep = mask.any(axis=0)
                corr = corr.loc[keep, keep]

                # Восстанавливаем диагональ
                np.fill_diagonal(corr.values, 1)

                
            if corr.empty or corr.shape[0] < 2:
                fig = None
            else:
                z = corr.values
                x = corr.columns.tolist()
                y = corr.index.tolist()
                annotations = [[f"{val:.2f}" if pd.notna(val) else "" for val in row] for row in z]

                fig = ff.create_annotated_heatmap(
                    z=z,
                    x=x,
                    y=y,
                    annotation_text=annotations,
                    colorscale="RdBu",
                    showscale=True
                )
                fig.update_layout(
                    title={
                        'text': f"Корреляционная матрица (|corr| > {threshold})",
                        'x': 0.5,
                        'xanchor': 'center',
                        'y': 0.97,
                        'yanchor': 'top'
                    },
                    margin=dict(t=140),  # увеличиваем верхний отступ
                    title_font=dict(size=18)
                )
        elif tab == "missing":
            missing = df.isna().sum()
            missing = missing[missing > 0].sort_values(ascending=False)

            if not missing.empty:
                fig = px.bar(
                    x=missing.index,
                    y=missing.values,
                    labels={"x": "Столбец", "y": "Количество пропущенных"},
                    title="Пропущенные значения по столбцам"
                )
            total_missing = df.isna().sum().sum()
            cols_with_nan = (df.isna().sum() > 0).sum()
            percent = (total_missing / (df.shape[0] * df.shape[1])) * 100

            stats = dbc.ListGroup([
                dbc.ListGroupItem(f"🔢 Всего пропущенных значений: {total_missing}"),
                dbc.ListGroupItem(f"📌 Столбцов с пропусками: {cols_with_nan}"),
                dbc.ListGroupItem(f"📉 Процент пропусков от всей таблицы: {percent:.2f}%")
            ])
        else:
            fig = None

        if tab == "missing":
            pass
        elif tab == "correlation":
            stats = html.Div("ℹ️ Корреляция рассчитывается по всем числовым столбцам.", style={"paddingTop": "10px"})
        else:
            summary = df[column].describe()
            if pd.api.types.is_numeric_dtype(df[column]):
                stats = dbc.ListGroup([
                    dbc.ListGroupItem(f"Количество значений: {summary['count']:.0f}"),
                    dbc.ListGroupItem(f"Среднее значение: {summary['mean']:.2f}"),
                    dbc.ListGroupItem(f"Стандартное отклонение: {summary['std']:.2f}"),
                    dbc.ListGroupItem(f"Минимум: {summary['min']:.2f}"),
                    dbc.ListGroupItem(f"25-й перцентиль: {summary['25%']:.2f}"),
                    dbc.ListGroupItem(f"Медиана (50%): {summary['50%']:.2f}"),
                    dbc.ListGroupItem(f"75-й перцентиль: {summary['75%']:.2f}"),
                    dbc.ListGroupItem(f"Максимум: {summary['max']:.2f}"),
                ])
            else:
                stats = dbc.ListGroup([
                    dbc.ListGroupItem(f"Количество значений: {summary['count']}"),
                    dbc.ListGroupItem(f"Уникальных значений: {summary['unique']}"),
                    dbc.ListGroupItem(f"Наиболее частое значение: {summary['top']}"),
                    dbc.ListGroupItem(f"Частота: {summary['freq']}"),
                ])

        if fig:
            graph = dcc.Graph(figure=fig)
        else:
            if tab == "missing":
                graph = html.Div("✅ Пропусков не найдено!", style={"color": "green", "paddingTop": "20px"})
            elif tab == "outliers":
                graph = html.Div("⚠️ Boxplot может быть построен только для числовых признаков.", style={"color": "darkred", "paddingTop": "20px"})
            elif tab == "distribution":
                graph = html.Div("⚠️ График не может быть построен для выбранных данных.", style={"color": "darkred", "paddingTop": "20px"})
            else:
                graph = html.Div("⚠️ Нет данных для отображения.", style={"color": "gray", "paddingTop": "20px"})

        return [graph], stats

    @app.callback(
        Output("corr-download", "data"),
        Input("download-btn", "n_clicks"),
        State("data-store", "data"),
        prevent_initial_call=True
    )
    def download_corr_matrix(n, data):
        if not data:
            return no_update
        df = pd.DataFrame(data)
        corr = df.select_dtypes("number").corr().round(3)
        return send_data_frame(corr.to_csv, filename="correlation_matrix.csv")
# callbacks/analysis.py
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from dash import Input, Output, State, dash_table, dcc, html, no_update


def register_analysis_callbacks(app):
    # 1. Вкладка "распределение" → выбор типа графика
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
                value="histogram",
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

    # 2. Выбор y для scatter
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

    # 3. Главный коллбэк построения графиков и статистики
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

        # Распределение
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

        # Выбросы
        elif tab == "outliers":
            if pd.api.types.is_numeric_dtype(df[column]):
                fig = px.box(df, y=column, points="outliers", title=f"Boxplot: {column}")
            else:
                fig = None

        # Корреляция
        elif tab == "correlation":
            corr = df.select_dtypes("number").corr().round(2)
            if threshold > 0:
                np.fill_diagonal(corr.values, 0)
                mask = corr.abs() >= threshold
                keep = mask.any(axis=0)
                corr = corr.loc[keep, keep]
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
                        'x': 0.5, 'y': 0.97,
                        'xanchor': 'center', 'yanchor': 'top'
                    },
                    margin=dict(t=140),  # увеличиваем верхний отступ
                    title_font=dict(size=18)
                )

        # Пропуски
        elif tab == "missing":
            missing = df.isna().sum()
            missing = missing[missing > 0].sort_values(ascending=False)
            fig = px.bar(x=missing.index, y=missing.values, title="Пропущенные значения по столбцам")
            total_missing = df.isna().sum().sum()
            cols_with_nan = (df.isna().sum() > 0).sum()
            percent = (total_missing / (df.shape[0] * df.shape[1])) * 100
            stats = dbc.ListGroup([
                dbc.ListGroupItem(f"🔢 Всего пропущенных значений: {total_missing}"),
                dbc.ListGroupItem(f"📌 Столбцов с пропусками: {cols_with_nan}"),
                dbc.ListGroupItem(f"📉 Процент пропусков от всей таблицы: {percent:.2f}%")
            ])
        
        elif tab == "duplicates":
            duplicated_rows = df[df.duplicated()]
            if not duplicated_rows.empty:
                dup_counts = df.duplicated(subset=None, keep=False).value_counts()
                count = df.duplicated().sum()

                fig = px.bar(
                    x=["Уникальные", "Дубликаты"],
                    y=[len(df) - count, count],
                    labels={"x": "Тип строк", "y": "Количество"},
                    title="Распределение дубликатов в датасете"
                )

            else:
                fig = None

            
            stats = dbc.ListGroup([
                dbc.ListGroupItem(f"📎 Кол-во дубликатов: {df.duplicated().sum()}"),
                dbc.ListGroupItem(f"🔢 Общее число строк: {len(df)}"),
                dbc.ListGroupItem(f"🧮 Уникальных строк: {len(df.drop_duplicates())}")
            ])


        
        else:
            fig = None

        # Блок статистики
        if tab == "missing":
            pass
        elif tab == "correlation":
            stats = html.Div("ℹ️ Корреляция рассчитывается по всем числовым столбцам.", style={"paddingTop": "10px"})
        elif tab == "duplicates":
            pass
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
                    dbc.ListGroupItem(f"Максимум: {summary['max']:.2f}")
                ])
            else:
                stats = dbc.ListGroup([
                    dbc.ListGroupItem(f"Количество значений: {summary['count']}"),
                    dbc.ListGroupItem(f"Уникальных значений: {summary['unique']}"),
                    dbc.ListGroupItem(f"Наиболее частое значение: {summary['top']}"),
                    dbc.ListGroupItem(f"Частота: {summary['freq']}")
                ])

        # График
        if fig:
            graph = dcc.Graph(figure=fig)
        else:
            message = {
                "missing": "✅ Пропусков не найдено!",
                "outliers": "⚠️ Boxplot может быть построен только для числовых признаков.",
                "distribution": "⚠️ График не может быть построен для выбранных данных."
            }.get(tab, "⚠️ Нет данных для отображения.")
            graph = html.Div(message, style={"color": "darkred", "paddingTop": "20px"})
        return [graph], stats

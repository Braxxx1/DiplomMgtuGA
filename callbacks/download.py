# callbacks/download.py
from dash import Input, Output, State, no_update
from dash.dcc import send_data_frame
import pandas as pd


def register_download_callbacks(app):
    @app.callback(
        Output("corr-download", "data"),
        Input("download-btn", "n_clicks"),
        State("data-store", "data"),
        prevent_initial_call=True
    )
    def download_corr_matrix(_, data):
        if not data:
            return no_update
        df = pd.DataFrame(data)
        corr = df.select_dtypes("number").corr().round(3)
        return send_data_frame(corr.to_csv, filename="correlation_matrix.csv", index=True)

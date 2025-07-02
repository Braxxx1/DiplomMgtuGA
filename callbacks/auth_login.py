# callbacks/auth_login.py
from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate
from callbacks.db import get_connection
import bcrypt

def register_login_callbacks(app):
    @app.callback(
        Output("login-message", "children"),
        Output("current-user", "data"),
        Output("url", "pathname"),
        Input("login-submit", "n_clicks"),
        State("login-email", "value"),
        State("login-password", "value"),
        prevent_initial_call=True
    )
    def login(_, email, password):
        if not email or not password:
            return "⚠️ Введите email и пароль", no_update, no_update

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, password_hash, role FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
            cursor.close()

            if not row:
                return "❌ Пользователь не найден", no_update, no_update

            user_id, name, password_hash, role = row.values()
            if not bcrypt.checkpw(password.encode(), password_hash.encode()):
                return "❌ Неверный пароль", no_update, no_update

            user_data = {"id": user_id, "name": name, "role": role}
            redirect_url = "/dashboard" if role == "teacher" else "/assignments"

            return "", user_data, redirect_url

        except Exception as e:
            return f"❌ Ошибка: {e}", no_update, no_update

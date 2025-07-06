# callbacks/auth_login.py
from dash import Input, Output, State, no_update, dcc
from dash.exceptions import PreventUpdate
from callbacks.db import get_connection
import bcrypt
import dash_bootstrap_components as dbc

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
            print("select")
            row = cursor.fetchone()
            cursor.close()

            if not row:
                return "❌ Пользователь не найден", no_update, no_update

            user_id, name, password_hash, role = row.values()
            if not bcrypt.checkpw(password.encode(), password_hash.encode()):
                return "❌ Неверный пароль", no_update, no_update

            user_data = {"id": user_id, "name": name, "role": role}
            redirect_url = "/profile" if role == "teacher" else "/profile"

            return "", user_data, redirect_url

        except Exception as e:
            return f"❌ Ошибка: {e}", no_update, no_update
        
    @app.callback(
        Output("current-user", "data", allow_duplicate=True),
        Output("url", "pathname", allow_duplicate=True),
        Input("logout-btn", "n_clicks"),
        State("current-user", "data"),
        prevent_initial_call=True
    )
    def logout(n_clicks, user):
        if not n_clicks or not user:
            raise PreventUpdate
        return None, "/login"

    # 👤 Обновление шапки с именем и кнопкой выхода
    @app.callback(
        Output("header-bar", "children"),
        Input("current-user", "data")
    )
    def update_header(user):
        print("🧠 Header user =", user)
        if not user:
            return ""

        name = user.get("name", "")
        role = user.get("role", "")
        role_name = "Преподаватель" if role == "teacher" else "Студент"

        return dbc.NavbarSimple([
            # dbc.NavItem(html.Span(f"👤 {role_name} {name}", className="me-3 text-white")),
            dbc.NavItem(dcc.Link(f"👤 Профиль", href="/profile", className="nav-link")),
            dbc.NavItem(dcc.Link("📊 Аналитика", href="/dashboard", className="nav-link")),
            dbc.NavItem(dcc.Link("⚙️ Предобработка", href="/preprocessing", className="nav-link")),
            dbc.Button("Выйти", id="logout-btn", color="light", size="sm", className="ms-3")
        ], brand="Data Dashboard", color="primary", dark=True, className="mb-4")

    
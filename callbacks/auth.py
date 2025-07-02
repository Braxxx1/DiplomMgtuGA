import mysql.connector
from dash import Input, Output, State, no_update
import bcrypt
from dash.exceptions import PreventUpdate
from callbacks.db import get_connection


def register_auth_callbacks(app):
    @app.callback(
    Output("reg-message", "children"),
    Input("reg-submit", "n_clicks"),
    State("reg-name", "value"),
    State("reg-email", "value"),
    State("reg-password", "value"),
    State("reg-role", "value"),
    prevent_initial_call=True
    )
    def register_user(n, name, email, password, role):

        if not all([name, email, password, role]):
            return "⚠️ Пожалуйста, заполните все поля."

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return "❌ Email уже зарегистрирован"

            import bcrypt
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
            """, (name, email, hashed, role))
            conn.commit()

            return "✅ Регистрация успешна!"

        except Exception as e:
            import traceback
            traceback.print_exc()  # Это покажет полный стек ошибки
            return f"❌ Ошибка: {e}"


        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
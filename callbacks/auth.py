from dash import Input, Output, State, no_update
import bcrypt
from dash.exceptions import PreventUpdate
from callbacks.db import get_connection
import pymysql


def register_auth_callbacks(app):
    @app.callback(
        Output("reg-message", "children"),
        Input("reg-submit", "n_clicks"),
        State("reg-name", "value"),
        State("reg-email", "value"),
        State("reg-password", "value"),
        State("reg-group", "value"),
        prevent_initial_call=True
    )
    def register_user(n, name, email, password, group_id):
        if not all([name, email, password, group_id]):
            return "⚠️ Пожалуйста, заполните все поля."

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Проверка email
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return "❌ Email уже зарегистрирован"

            # Хешируем пароль
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            # Добавляем нового пользователя
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role, group_id)
                VALUES (%s, %s, %s, 'student', %s)
            """, (name, email, hashed, group_id))
            conn.commit()

            return "✅ Регистрация успешна!"

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"❌ Ошибка: {e}"

        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass

    @app.callback(
        Output("reg-group", "options"),
        Input("reg-submit", "n_clicks"),
        prevent_initial_call="initial_duplicate"
    )
    def load_group_options(_):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM student_groups")
            groups = cursor.fetchall()
            return [{"label": g["name"], "value": g["id"]} for g in groups]
        except Exception as e:
            print("Ошибка при загрузке групп:", e)
            return []
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass


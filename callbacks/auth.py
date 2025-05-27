#pip install bcrypt
import mysql.connector
from dash import Input, Output, State, no_update
import bcrypt
from dash.exceptions import PreventUpdate

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
        print("⚙️ Коллбэк сработал")

        if not all([name, email, password, role]):
            print("❌ Не все поля заполнены")
            return "⚠️ Пожалуйста, заполните все поля."

        try:
            print("🔌 Подключаемся к MySQL...")
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="KAgdeckeywukMe0",
                database="analizeprog",
                port=3306,
                connection_timeout=5
            )
            cursor = conn.cursor()
            print("✅ Соединение установлено")

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
            print("❌ Ошибка:", e)
            traceback.print_exc()  # Это покажет полный стек ошибки
            return f"❌ Ошибка: {e}"


        finally:
            try:
                cursor.close()
                conn.close()
                print("🔒 Соединение закрыто")
            except:
                pass

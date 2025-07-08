from dash import Input, Output, State, html, dcc, ctx, callback_context, no_update, MATCH, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from callbacks.db import get_connection
from datetime import datetime


def register_test_callbacks(app):
    # Загрузка теста и вопросов
    @app.callback(
        Output("selected-test-id", "data"),
        Output("test-questions-store", "data"),
        Input("url", "search")#,
        # prevent_initial_call=True
    )
    def extract_test_id_and_load_questions(query):
        from urllib.parse import parse_qs
        print(1)
        qs = parse_qs(query.lstrip("?"))
        test_id = qs.get("id", [None])[0]
        print(qs, test_id)
        if not test_id:
            raise PreventUpdate

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, question FROM questions WHERE test_id = %s", (test_id,))
            questions = cursor.fetchall()
            return test_id, questions
        except Exception as e:
            print("Ошибка при загрузке вопросов:", e)
            return test_id, []
        finally:
            cursor.close()
            conn.close()

    # Отображение текущего вопроса
    @app.callback(
        Output("test-question-form", "children"),
        Input("test-questions-store", "data"),
        Input("current-question-index", "data"),
        prevent_initial_call=True
    )
    def render_single_question(questions, index):
        
        if not questions or index is None:
            raise PreventUpdate

        total = len(questions)
        q = questions[index]
        content = dbc.Card([
            dbc.CardBody([
                html.H5(f"Вопрос {index+1} из {total}", className="text-center text-muted"),
                html.H4(q["question"], className="text-center mb-3"),
                dcc.Textarea(
                    id={"type": "answer-input", "index": q["id"]},
                    className="form-control",
                    style={"width": "100%", "minHeight": "100px"}
                )
            ])
        ], className="mb-4 shadow")

        buttons = [
            dbc.Button("← Назад", id="prev-question-btn", color="secondary", className="me-2",
                    style={"display": "none" if index == 0 else "block"}),
            dbc.Button("Далее →", id="next-question-btn", color="primary",
                    style={"display": "none" if index == total - 1 else "block"}),
            dbc.Button("✅ Завершить", id="submit-test-btn", color="success",
                    style={"display": "block" if index == total - 1 else "none"})
        ]


        return html.Div([
            content,
            html.Div(buttons, className="d-flex justify-content-center"),
            html.Div(id="test-submit-msg", className="mt-3 text-center")
        ])

    # Управление переключением вопросов
    @app.callback(
        Output("current-question-index", "data"),
        Input("prev-question-btn", "n_clicks"),
        Input("next-question-btn", "n_clicks"),
        State("current-question-index", "data"),
        State("test-questions-store", "data"),
        prevent_initial_call=True
    )
    def update_question_index(prev_clicks, next_clicks, current_index, questions):
        triggered = ctx.triggered_id
        if not questions:
            return no_update
        
        max_index = len(questions) - 1
        if triggered == "next-question-btn" and current_index < max_index:
            return current_index + 1
        elif triggered == "prev-question-btn" and current_index > 0:
            return current_index - 1

        return no_update
    
    @app.callback(
        Output("answers-store", "data", allow_duplicate=True),
        Input({"type": "answer-input", "index": ALL}, "value"),
        State("answers-store", "data"),
        State("test-questions-store", "data"),
        Input("current-question-index", "data"),
        prevent_initial_call=True
    )
    def update_answers(values, store, questions, index):
        if store is None:
            store = {}

        # for question, value in zip(questions, values):
        #     if value is not None:
        store[str(questions[index]["id"])] = values[0]
        return store
        
    
    @app.callback(
        Output("test-submit-msg", "children"),
        Input("submit-test-btn", "n_clicks"),
        State("answers-store", "data"),
        State("test-questions-store", "data"),
        State("selected-test-id", "data"),
        State("current-user", "data"),
        prevent_initial_call=True
    )
    def submit_answers(_, answers_store, questions, test_id, user):
        print(user, questions, answers_store)
        if not user or not questions or not answers_store:
            return "❌ Ошибка: недостаточно данных."

        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 💡 Удалим предыдущие ответы студента
            cursor.execute("""
                DELETE FROM answers WHERE test_id = %s AND student_id = %s
            """, (test_id, user["id"]))
            
            for q in questions:
                qid = str(q["id"])
                if qid in answers_store:
                    cursor.execute("""
                        INSERT INTO answers (test_id, student_id, question_id, answer)
                        VALUES (%s, %s, %s, %s)
                    """, (test_id, user["id"], q["id"], answers_store[qid]))
                    
            cursor.execute("""
                INSERT INTO test_status (test_id, student_id, submitted_at, status)
                VALUES (%s, %s, NOW(), 'pending')
                ON DUPLICATE KEY UPDATE
                    submitted_at = NOW(),
                    status = 'pending'
            """, (test_id, user["id"]))
            
            conn.commit()
            return "✅ Ответы успешно отправлены!"
        except Exception as e:
            print("Ошибка при сохранении ответов:", e)
            return f"❌ Ошибка: {e}"
        finally:
            cursor.close()
            conn.close()

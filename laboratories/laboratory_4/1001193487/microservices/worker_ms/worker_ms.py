from celery import Celery, Task
from flask import Flask, request, jsonify
from celery import shared_task

from celery.result import AsyncResult

# Add module-level FlaskTask for pickling
class FlaskTask(Task):
    def __call__(self, *args, **kwargs):
        with self._app.app_context():
            return super().__call__(*args, **kwargs)

def celery_init_app(app: Flask) -> Celery:
    celery_app = Celery(app.name, task_cls=FlaskTask)
    FlaskTask._app = app
    celery_app.app_context = app.app_context
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://redis",
            result_backend="redis://redis",
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)
    return app

flask_app = create_app()
celery_app = flask_app.extensions["celery"]

@flask_app.get("/result/<id>")
def task_result(id: str) -> tuple:
    result = AsyncResult(id)
    print({
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if result.ready() else None,
    })
    return jsonify({
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if result.ready() else None,
    }), 200

@shared_task(ignore_result=False)
def add_together(a: int, b: int) -> int:
    return a + b

@flask_app.post("/add")
def start_add() -> tuple:
    data = request.json
    if not all(k in data for k in ("a", "b")):
        return jsonify({"error": "Missing parameters"}), 400
    a = data["a"]
    b = data["b"]
    result = add_together.delay(a, b)
    return jsonify({"result_id": result.id}), 201


if __name__ == "__main__":
    flask_app.run(debug=True, port=80, host="0.0.0.0")
import os, textwrap
from .index_routes import INDEX_ROUTES
from .generate_queue import (
    write_wait_for_it_script,
    generate_producer,
    generate_consumer,
)


def generate_backend(name, database=None, database_type=None, connections=None):
    print(
        f"Generating backend for {name} with database {database} and type {database_type}"
    )
    path = f"skeleton/{name}"
    os.makedirs(path, exist_ok=True)

    # Default simple app
    app_code = textwrap.dedent(
        """
        from flask import Flask, jsonify

        app = Flask(__name__)

        @app.route('/')
        def hello():
            return jsonify({"message": "Hello World from Backend"})

        if __name__ == '__main__':
            app.run(host='0.0.0.0', port=80)
    """
    )

    requirements = ["flask"]

    # Only add connection code if this is a "from" component in a connector
    print("Generating backend with connections: " + str(connections))
    if connections:
        for conn_type, target in connections.items():
            if conn_type == "kafka_connector_reverse" and target:
                write_wait_for_it_script(path)
                generate_consumer(name, target)
                return
            elif conn_type == "kafka_connector" and target:
                write_wait_for_it_script(path)
                generate_producer(name, target)
                return
            elif conn_type == "db_connector" and target:
                try:
                    index_route_data = INDEX_ROUTES[database_type.lower()]
                    requirements.extend(index_route_data["requirements"])
                    app_code = textwrap.dedent(
                        f"""
from flask import Flask, jsonify


app = Flask(__name__)

{index_route_data['code'](target)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
                    """
                    )
                except KeyError:
                    requirements.append("mysql-connector-python")
                    app_code = textwrap.dedent(
                        """
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({{"message": "Hello World from Backend", "database_connection": "not configured", "type": "Unknown"}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
                    """
                    )

    with open(os.path.join(path, "app.py"), "w", encoding="utf8") as f:
        f.write(app_code)

    with open(os.path.join(path, "Dockerfile"), "w", encoding="utf8") as f:
        requirements_str = " ".join(requirements)
        f.write(
            textwrap.dedent(
                f"""
            FROM python:3.11-slim
                                
            WORKDIR /app
            COPY . .
            RUN pip install {requirements_str}
                                
            CMD ["python", "app.py"]
            """
            )
        )

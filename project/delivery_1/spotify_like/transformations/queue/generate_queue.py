import os, textwrap


def write_wait_for_it_script(path):
    wait_for_it_code = textwrap.dedent(
        """
        #!/usr/bin/env bash
        # Use this script to test if a given TCP host/port are available

        WAITFORIT_cmdname=${0##*/}

        echoerr() { if [[ $WAITFORIT_QUIET -ne 1 ]]; then echo "$@" 1>&2; fi }

        usage()
        {
            cat << USAGE >&2
        Usage:
            $WAITFORIT_cmdname host:port [-s] [-t timeout] [-- command args]
            -h HOST | --host=HOST       Host or IP under test
            -p PORT | --port=PORT       TCP port under test
                                        Alternatively, you specify the host and port as host:port
            -s | --strict               Only execute subcommand if the test succeeds
            -q | --quiet                Don't output any status messages
            -t TIMEOUT | --timeout=TIMEOUT
                                        Timeout in seconds, zero for no timeout
            -- COMMAND ARGS             Execute command with args after the test finishes
        USAGE
            exit 1
        }

        wait_for()
        {
            if [[ $WAITFORIT_TIMEOUT -gt 0 ]]; then
                echoerr "$WAITFORIT_cmdname: waiting $WAITFORIT_TIMEOUT seconds for $WAITFORIT_HOST:$WAITFORIT_PORT"
            else
                echoerr "$WAITFORIT_cmdname: waiting for $WAITFORIT_HOST:$WAITFORIT_PORT without a timeout"
            fi
            WAITFORIT_start_ts=$(date +%s)
            while :
            do
                if [[ $WAITFORIT_ISBUSY -eq 1 ]]; then
                    nc -z $WAITFORIT_HOST $WAITFORIT_PORT
                    WAITFORIT_result=$?
                else
                    (echo -n > /dev/tcp/$WAITFORIT_HOST/$WAITFORIT_PORT) >/dev/null 2>&1
                    WAITFORIT_result=$?
                fi
                if [[ $WAITFORIT_result -eq 0 ]]; then
                    WAITFORIT_end_ts=$(date +%s)
                    echoerr "$WAITFORIT_cmdname: $WAITFORIT_HOST:$WAITFORIT_PORT is available after $((WAITFORIT_end_ts - WAITFORIT_start_ts)) seconds"
                    break
                fi
                sleep 1
            done
            return $WAITFORIT_result
        }

        wait_for_wrapper()
        {
            # In order to support SIGINT during timeout: http://unix.stackexchange.com/a/57692
            if [[ $WAITFORIT_QUIET -eq 1 ]]; then
                timeout $WAITFORIT_BUSYTIMEFLAG $WAITFORIT_TIMEOUT $0 --quiet --child --host=$WAITFORIT_HOST --port=$WAITFORIT_PORT --timeout=$WAITFORIT_TIMEOUT &
            else
                timeout $WAITFORIT_BUSYTIMEFLAG $WAITFORIT_TIMEOUT $0 --child --host=$WAITFORIT_HOST --port=$WAITFORIT_PORT --timeout=$WAITFORIT_TIMEOUT &
            fi
            WAITFORIT_PID=$!
            trap "kill -INT -$WAITFORIT_PID" INT
            wait $WAITFORIT_PID
            WAITFORIT_RESULT=$?
            if [[ $WAITFORIT_RESULT -ne 0 ]]; then
                echoerr "$WAITFORIT_cmdname: timeout occurred after waiting $WAITFORIT_TIMEOUT seconds for $WAITFORIT_HOST:$WAITFORIT_PORT"
            fi
            return $WAITFORIT_RESULT
        }

        # process arguments
        while [[ $# -gt 0 ]]
        do
            case "$1" in
                *:* )
                WAITFORIT_hostport=(${1//:/ })
                WAITFORIT_HOST=${WAITFORIT_hostport[0]}
                WAITFORIT_PORT=${WAITFORIT_hostport[1]}
                shift 1
                ;;
                --child)
                WAITFORIT_CHILD=1
                shift 1
                ;;
                -q | --quiet)
                WAITFORIT_QUIET=1
                shift 1
                ;;
                -s | --strict)
                WAITFORIT_STRICT=1
                shift 1
                ;;
                -h)
                WAITFORIT_HOST="$2"
                if [[ $WAITFORIT_HOST == "" ]]; then break; fi
                shift 2
                ;;
                --host=*)
                WAITFORIT_HOST="${1#*=}"
                shift 1
                ;;
                -p)
                WAITFORIT_PORT="$2"
                if [[ $WAITFORIT_PORT == "" ]]; then break; fi
                shift 2
                ;;
                --port=*)
                WAITFORIT_PORT="${1#*=}"
                shift 1
                ;;
                -t)
                WAITFORIT_TIMEOUT="$2"
                if [[ $WAITFORIT_TIMEOUT == "" ]]; then break; fi
                shift 2
                ;;
                --timeout=*)
                WAITFORIT_TIMEOUT="${1#*=}"
                shift 1
                ;;
                --)
                shift
                WAITFORIT_CLI=("$@")
                break
                ;;
                --help)
                usage
                ;;
                *)
                echoerr "Unknown argument: $1"
                usage
                ;;
            esac
        done

        if [[ "$WAITFORIT_HOST" == "" || "$WAITFORIT_PORT" == "" ]]; then
            echoerr "Error: you need to provide a host and port to test."
            usage
        fi

        WAITFORIT_TIMEOUT=${WAITFORIT_TIMEOUT:-15}
        WAITFORIT_STRICT=${WAITFORIT_STRICT:-0}
        WAITFORIT_CHILD=${WAITFORIT_CHILD:-0}
        WAITFORIT_QUIET=${WAITFORIT_QUIET:-0}

        # Check to see if timeout is from busybox?
        WAITFORIT_TIMEOUT_PATH=$(type -p timeout)
        WAITFORIT_TIMEOUT_PATH=$(realpath $WAITFORIT_TIMEOUT_PATH 2>/dev/null || readlink -f $WAITFORIT_TIMEOUT_PATH)

        WAITFORIT_BUSYTIMEFLAG=""
        if [[ $WAITFORIT_TIMEOUT_PATH =~ "busybox" ]]; then
            WAITFORIT_ISBUSY=1
            # Check if busybox timeout uses -t flag
            # (recent Alpine versions don't support -t anymore)
            if timeout &>/dev/stdout | grep -q -e '-t '; then
                WAITFORIT_BUSYTIMEFLAG="-t"
            fi
        else
            WAITFORIT_ISBUSY=0
        fi

        if [[ $WAITFORIT_CHILD -gt 0 ]]; then
            wait_for
            WAITFORIT_RESULT=$?
            exit $WAITFORIT_RESULT
        else
            if [[ $WAITFORIT_TIMEOUT -gt 0 ]]; then
                wait_for_wrapper
                WAITFORIT_RESULT=$?
            else
                wait_for
                WAITFORIT_RESULT=$?
            fi
        fi

        if [[ $WAITFORIT_CLI != "" ]]; then
            if [[ $WAITFORIT_RESULT -ne 0 && $WAITFORIT_STRICT -eq 1 ]]; then
                echoerr "$WAITFORIT_cmdname: strict mode, refusing to execute subprocess"
                exit $WAITFORIT_RESULT
            fi
            exec "${WAITFORIT_CLI[@]}"
        else
            exit $WAITFORIT_RESULT
        fi
    """
    )

    with open(os.path.join(path, "wait-for-it.sh"), "w", encoding="utf8") as f:
        f.write(wait_for_it_code)
    os.chmod(os.path.join(path, "wait-for-it.sh"), 0o755)  # Make it executable


def generate_consumer(name):
    path = f"skeleton/{name}"
    os.makedirs(path, exist_ok=True)

    app_code = textwrap.dedent(
        """
        from flask import Flask
        from kafka import KafkaConsumer
        import os
        import threading

        app = Flask(__name__)

        KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
        KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "upload-topic")
        GROUP_ID = os.getenv("GROUP_ID", "saver-group")
        SAVE_PATH = os.getenv("SAVE_PATH", "/tmp")

        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            group_id=GROUP_ID,
            auto_offset_reset="earliest",
        )


        def consume_loop():
            for message in consumer:
                filename = os.path.join(SAVE_PATH, "received_file")
                print(f"Saving file to {filename}")
                with open(filename, "wb") as f:
                    f.write(message.value)


        # Start consumer loop in a separate thread
        threading.Thread(target=consume_loop, daemon=True).start()


        @app.route("/health", methods=["GET"])
        def health_check():
            return {"status": "consumer running"}, 200


        if __name__ == "__main__":
            app.run(host="0.0.0.0", port=5001)
    """
    )

    requirements = ["flask", "kafka-python"]

    with open(os.path.join(path, "app.py"), "w", encoding="utf8") as f:
        f.write(app_code)

    write_wait_for_it_script(path)

    with open(os.path.join(path, "Dockerfile"), "w", encoding="utf8") as f:
        requirements_str = "\n".join([f"RUN pip install {req}" for req in requirements])
        f.write(
            textwrap.dedent(
                f"""
            FROM python:3.11-slim
            WORKDIR /app
            COPY . /app

            RUN chmod +x /app/wait-for-it.sh

            RUN apt-get update && apt-get install -y netcat-traditional
            {requirements_str}

            ENTRYPOINT ["/app/wait-for-it.sh", "kafka:9092", "--timeout=30", "--strict", "--"]
        """
            )
        )


def generate_producer(name):
    path = f"skeleton/{name}"
    os.makedirs(path, exist_ok=True)

    app_code = textwrap.dedent(
        """
        from flask import Flask, request, jsonify
        from kafka import KafkaProducer
        import os

        app = Flask(__name__)

        KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
        KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "upload-topic")

        producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)


        @app.route("/upload", methods=["POST"])
        def upload_file():
            file = request.files.get("file")
            if file:
                producer.send(KAFKA_TOPIC, file.read())
                return jsonify({"status": "file uploaded"}), 200
            return jsonify({"error": "No file provided"}), 400


        if __name__ == "__main__":
            app.run(host="0.0.0.0", port=5000)
    """
    )

    requirements = ["flask", "kafka-python"]

    with open(os.path.join(path, "app.py"), "w", encoding="utf8") as f:
        f.write(app_code)

    write_wait_for_it_script(path)

    with open(os.path.join(path, "Dockerfile"), "w", encoding="utf8") as f:
        requirements_str = "\n".join([f"RUN pip install {req}" for req in requirements])
        f.write(
            textwrap.dedent(
                f"""
            FROM python:3.11-slim
            WORKDIR /app
            COPY . /app

            RUN chmod +x /app/wait-for-it.sh

            RUN apt-get update && apt-get install -y netcat-traditional
            {requirements_str}

            ENTRYPOINT ["/app/wait-for-it.sh", "kafka:9092", "--timeout=30", "--strict", "--"]
        """
            )
        )

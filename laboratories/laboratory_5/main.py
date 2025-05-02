import multiprocessing
import os
from Components import api_gateway, cache, database, load_balancer_ms, login_microservice, microservice, worker, \
    load_balancer
import config

def apply_rate_limit_config(service_name):
    cfg = config.RATE_LIMIT_CONFIG[service_name]
    os.environ["MAX_REQUESTS_PER_TIME"] = str(cfg["MAX_REQUESTS_PER_TIME"])
    os.environ["RATE_LIMIT_TIME"] = str(cfg["RATE_LIMIT_TIME"])


def run_login_microservice(port):
    apply_rate_limit_config("login")
    login_microservice.app.run(port=port, debug=False, use_reloader=False)

def run_cache_service(port):
    apply_rate_limit_config("cache")
    cache.app.run(port=port, debug=False, use_reloader=False)

def run_db_service(port):
    apply_rate_limit_config("db")
    database.app.run(port=port, debug=False, use_reloader=False)

def run_microservice_B(port):
    apply_rate_limit_config("microservice_B")
    microservice.app.run(port=port, debug=False, use_reloader=False)

def run_microservice_A(port):
    apply_rate_limit_config("microservice_A")
    microservice.app.run(port=port, debug=False, use_reloader=False)

def run_worker(port):
    apply_rate_limit_config("worker")
    worker.app.run(port=port, debug=False, use_reloader=False)

def run_app_service(port):
    apply_rate_limit_config("gateway")
    api_gateway.app.run(port=port, debug=False, use_reloader=False)

def run_load_balancer(port):
    apply_rate_limit_config("load_balancer")
    load_balancer.app.run(port=port, debug=False, use_reloader=False)


def run_load_balancer_ms(port):
    apply_rate_limit_config("load_balancer")
    load_balancer_ms.app.run(port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    multiprocessing.freeze_support()

    processes = [
        multiprocessing.Process(target=run_login_microservice, args=(5009,)),
        multiprocessing.Process(target=run_cache_service, args=(5004,)),
        multiprocessing.Process(target=run_db_service, args=(5002,)),
        multiprocessing.Process(target=run_microservice_A, args=(5001,)),
        multiprocessing.Process(target=run_microservice_B, args=(5006,)),# MS powerful
        # multiprocessing.Process(target=run_microservice_A, args=(5006,)),  # MS normal
        multiprocessing.Process(target=run_worker, args=(5005,)),
        multiprocessing.Process(target=run_app_service, args=(5000,)),   #  gateway
        multiprocessing.Process(target=run_app_service, args=(5003,)),  #  gateway
        multiprocessing.Process(target=run_load_balancer, args=(8000,)),
        multiprocessing.Process(target=run_load_balancer_ms, args=(8001,))# otro lb
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()


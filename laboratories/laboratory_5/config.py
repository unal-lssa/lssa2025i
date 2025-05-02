# config.py

# Configuración básica
BASIC = {
    "login": {
        "MAX_REQUESTS_PER_TIME": 5,
        "RATE_LIMIT_TIME": 60
    },
    "cache": {
        "MAX_REQUESTS_PER_TIME": 1,
        "RATE_LIMIT_TIME": 30
    },
    "db": {
        "MAX_REQUESTS_PER_TIME": 5,
        "RATE_LIMIT_TIME": 60
    },
    "microservice_A": {
        "MAX_REQUESTS_PER_TIME": 10,
        "RATE_LIMIT_TIME": 60
    },
    "microservice_B": {
        "MAX_REQUESTS_PER_TIME": 10,
        "RATE_LIMIT_TIME": 60
    },
    "worker": {
        "MAX_REQUESTS_PER_TIME": 10,
        "RATE_LIMIT_TIME": 60
    },
    "gateway": {
        "MAX_REQUESTS_PER_TIME": 12,
        "RATE_LIMIT_TIME": 60
    },
    "load_balancer": {
        "MAX_REQUESTS_PER_TIME": 1000,
        "RATE_LIMIT_TIME": 60
    }
}

# Configuración media
ADVANCED = {
    "login": {
        "MAX_REQUESTS_PER_TIME": 100,
        "RATE_LIMIT_TIME": 60
    },
    "cache": {
        "MAX_REQUESTS_PER_TIME": 10000,
        "RATE_LIMIT_TIME": 30
    },
    "db": {
        "MAX_REQUESTS_PER_TIME": 150,
        "RATE_LIMIT_TIME": 60
    },
    "microservice_A": {
        "MAX_REQUESTS_PER_TIME": 50,
        "RATE_LIMIT_TIME": 60
    },
    "microservice_B": {
        "MAX_REQUESTS_PER_TIME": 50,
        "RATE_LIMIT_TIME": 60
    },
    "worker": {
        "MAX_REQUESTS_PER_TIME": 200,
        "RATE_LIMIT_TIME": 60
    },
    "gateway": {
        "MAX_REQUESTS_PER_TIME": 120,
        "RATE_LIMIT_TIME": 60
    },
    "load_balancer": {
        "MAX_REQUESTS_PER_TIME": 10000,
        "RATE_LIMIT_TIME": 60
    }
}

# Configuración poderosa
POWERFUL = {
    "login": {
        "MAX_REQUESTS_PER_TIME": 100,
        "RATE_LIMIT_TIME": 60
    },
    "cache": {
        "MAX_REQUESTS_PER_TIME": 10000,
        "RATE_LIMIT_TIME": 30
    },
    "db": {
        "MAX_REQUESTS_PER_TIME": 150,
        "RATE_LIMIT_TIME": 60
    },
    "microservice_A": {
        "MAX_REQUESTS_PER_TIME": 1000,
        "RATE_LIMIT_TIME": 60
    },
    "microservice_B": {
        "MAX_REQUESTS_PER_TIME": 50,
        "RATE_LIMIT_TIME": 60
    },
    "worker": {
        "MAX_REQUESTS_PER_TIME": 200,
        "RATE_LIMIT_TIME": 60
    },
    "gateway": {
        "MAX_REQUESTS_PER_TIME": 120,
        "RATE_LIMIT_TIME": 60
    },
    "load_balancer": {
        "MAX_REQUESTS_PER_TIME": 10000,
        "RATE_LIMIT_TIME": 60
    }
}

# Selección de configuración activa
RATE_LIMIT_CONFIG = POWERFUL
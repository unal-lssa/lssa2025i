# ----------------------------------------------
# General Configuration
# ----------------------------------------------
COMPOSE=docker-compose -f docker-compose.yml
VENV=.venv
PYTHON=$(VENV)/bin/python3
LOCUST_BIN=$(VENV)/bin/locust
LOCUST_BASE=$(LOCUST_BIN) -f tests/load_test.py --host=http://localhost:8000 --headless --users 600 --spawn-rate 60 --run-time 60s

# ----------------------------------------------
# Python, pip, and venv validation and setup
# ----------------------------------------------
check-python:
	@command -v python3 >/dev/null 2>&1 || { \
		echo "❌ Python3 is not installed."; \
		echo "👉 Install it manually:"; \
		echo " - Ubuntu: sudo apt install python3 python3-venv"; \
		echo " - Mac: brew install python3"; \
		echo " - Windows: https://www.python.org/downloads/"; \
		exit 1; \
	}
	@echo "✅ Python is installed."

check-pip:
	@command -v pip3 >/dev/null 2>&1 || command -v pip >/dev/null 2>&1 || { \
		echo "❌ pip is not installed."; \
		echo "👉 Try: sudo apt install python3-pip"; \
		exit 1; \
	}
	@echo "✅ pip is installed."

check-venv:
	@python3 -m venv --help >/dev/null 2>&1 || { \
		echo "❌ Python venv module is not available."; \
		echo "👉 Please install it manually:"; \
		echo " - Ubuntu/Debian: sudo apt install python3-venv"; \
		echo " - Mac: brew install python3 (includes venv)"; \
		echo " - Windows: venv should be included by default"; \
		exit 1; \
	}
	@echo "✅ Python venv is available."

venv:
	@if [ ! -d ".venv" ]; then \
		echo "🛠️  Creating Python virtual environment..."; \
		python3 -m venv .venv; \
	else \
		echo "✅ .venv already exists."; \
	fi

install: check-python check-pip check-venv venv
	@echo "📦 Installing Python dependencies into .venv..."
	. .venv/bin/activate && .venv/bin/pip install -r tests/requirements.txt
	@echo "✅ Dependencies installed."


# ----------------------------------------------
# Launch services with 1, 2, or 3 API Gateway instances
# ----------------------------------------------
up1: down
	@echo "🚀 Starting services with 1 API Gateway instance..."
	$(COMPOSE) up --build -d \
		load_balancer \
		api-gateway-1 \
		cache \
		database \
		microservice \
		worker
	@echo "✅ All services are up (1 Gateway)."

up2: down
	@echo "🚀 Starting services with 2 API Gateway instances..."
	$(COMPOSE) up --build -d \
		load_balancer \
		api-gateway-1 \
		api-gateway-2 \
		cache \
		database \
		microservice \
		worker
	@echo "✅ All services are up (2 Gateways)."

up3: down
	@echo "🚀 Starting services with 3 API Gateway instances..."
	$(COMPOSE) up --build -d \
		load_balancer \
		api-gateway-1 \
		api-gateway-2 \
		api-gateway-3 \
		cache \
		database \
		microservice \
		worker
	@echo "✅ All services are up (3 Gateways)."

down:
	@echo "🧹 Shutting down all services..."
	$(COMPOSE) down
	@echo "✅ All services are stopped."


# ----------------------------------------------
# Extended Load testing with Locust (cache modes)
# ----------------------------------------------
test1-hit:
	@echo "📊 Running load test with 1 API Gateway [Cache HIT]..."
	$(LOCUST_BASE) --csv=tests/results/results_1_gateway_hit --mode=hit || true
	@echo "✅ Test completed: results_1_gateway_hit*.csv"

test1-miss:
	@echo "📊 Running load test with 1 API Gateway [Cache MISS]..."
	$(LOCUST_BASE) --csv=tests/results/results_1_gateway_miss --mode=miss || true
	@echo "✅ Test completed: results_1_gateway_miss*.csv"

test2-hit:
	@echo "📊 Running load test with 2 API Gateways [Cache HIT]..."
	$(LOCUST_BASE) --csv=tests/results/results_2_gateways_hit --mode=hit || true
	@echo "✅ Test completed: results_2_gateways_hit*.csv"

test2-miss:
	@echo "📊 Running load test with 2 API Gateways [Cache MISS]..."
	$(LOCUST_BASE) --csv=tests/results/results_2_gateways_miss --mode=miss || true
	@echo "✅ Test completed: results_2_gateways_miss*.csv"

test3-hit:
	@echo "📊 Running load test with 3 API Gateways [Cache HIT]..."
	$(LOCUST_BASE) --csv=tests/results/results_3_gateways_hit --mode=hit || true
	@echo "✅ Test completed: results_3_gateways_hit*.csv"

test3-miss:
	@echo "📊 Running load test with 3 API Gateways [Cache MISS]..."
	$(LOCUST_BASE) --csv=tests/results/results_3_gateways_miss --mode=miss || true
	@echo "✅ Test completed: results_3_gateways_miss*.csv"

# ----------------------------------------------
# Benchmark Combined run: up → test (by mode) → down
# ----------------------------------------------

benchmark-all:
	@echo "📊 Running simple benchmark (1 vs 3 gateways)..."
	@make clean

# Init with 1 gateway and wark up
	@make up1
	@echo "🔄 Warm-up: 10s hitting /data..."
	$(LOCUST_BIN) -f tests/load_test.py --host=http://localhost:8000 --headless --users 10 --spawn-rate 5 --run-time 10s --mode=miss || true

	@make test1-miss
	@make test1-hit

# Init with 1 gateway and wark up
	@make up3
	@echo "🔄 Warm-up: 10s hitting /data..."
	$(LOCUST_BIN) -f tests/load_test.py --host=http://localhost:8000 --headless --users 10 --spawn-rate 5 --run-time 10s --mode=miss || true

	@make test3-miss
	@make test3-hit

	@make down
	@make report
	@echo "✅ Simple benchmark complete."

report:
	@echo "🧠 Generating graphs and summary report..."
	$(PYTHON) tests/generate_graphs.py
	@echo "✅ Report ready at tests/reports/summary.md"


# ----------------------------------------------
# Utility commands
# ----------------------------------------------
logs:
	@echo "📄 Showing live logs..."
	$(COMPOSE) logs -f

ps:
	@echo "📦 Showing running containers..."
	$(COMPOSE) ps

clean:
	@echo "🧽 Cleaning up containers and volumes..."
	$(COMPOSE) down -v --remove-orphans
	@echo "✅ Cleanup complete."

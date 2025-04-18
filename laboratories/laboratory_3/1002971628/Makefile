.SILENT:
.PHONY: valid-request invalid-request full-valid-request invalid-external-request init run stop rate-limit-request

init:
	docker compose build
	docker pull postgres:16
	docker pull curlimages/curl

run:
	docker compose up -d

stop:
	docker compose down

valid-login-request:
	curl -X POST -H "Content-Type: application/json" \
	     -d '{"username": "user1", "password": "password123"}' \
	     http://localhost:8080/login

invalid-login-request:
	curl -X POST -H "Content-Type: application/json" \
	     -d '{"username": "user2", "password": "password12"}' \
	     http://localhost:8080/login

full-valid-request:
	@token=$$(curl -s -X POST -H "Content-Type: application/json" \
	     -d '{"username": "user1", "password": "password123"}' \
	     http://localhost:8080/login | \
	     grep -o '"token":"[^"]*"' | cut -d'"' -f4); \
	curl -X GET -H "Authorization: Bearer $$token" \
	http://localhost:8080/data

invalid-external-request:
	docker compose run --rm invalid_request

rate-limit-request:
	@echo "Sending 15 consecutive requests to test rate limiting"
	@for i in $$(seq 1 15); do \
		echo "Request $$i:"; \
		curl -s -X POST -H "Content-Type: application/json" \
		-d '{"username": "user1", "password": "password123"}' \
		http://localhost:8080/login \
		-w "\nStatus: %{http_code}\nTime: %{time_total}s\n"; \
		echo "--------------------------"; \
	done

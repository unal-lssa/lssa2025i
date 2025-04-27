
image_name := lssa_delivery_1

build: 
	docker build -t $(image_name) .

generate:
	docker run --rm -v "$PWD:/app" $(image_name)


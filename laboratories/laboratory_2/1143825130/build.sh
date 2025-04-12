#!/bin/bash

docker build -t lssa-lab2 .
docker run --rm -v "$PWD:/app" lssa-lab2
cd skeleton
docker compose up --build

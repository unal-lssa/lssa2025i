FROM python:3.9-alpine

WORKDIR /app

RUN apk update && \
    apk add --no-cache \
        gcc \
        musl-dev \
        python3-dev && \
    rm -rf /var/cache/apk/*

RUN pip install --no-cache-dir \
    Flask==3.1.0  \
    PyJWT==2.10.1 

COPY api-gateway.py .

ENV SECRET_KEY=kS1p_UhHHit_dOmJw1JO1e6PiQLV0xlF7bq5O4U65bw
ENV AUTHORIZED_IP=172.18.0.1 


CMD ["python", "api-gateway.py"]
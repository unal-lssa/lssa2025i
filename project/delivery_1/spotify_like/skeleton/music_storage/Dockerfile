FROM localstack/localstack:s3-latest
RUN apt-get update && \
    apt-get install -y python3-pip curl && \
    pip3 install awscli awscli-local

COPY init-bucket.sh /etc/localstack/init/ready.d/init-bucket.sh
COPY ./song.mp3 /songs/
RUN chmod +x /etc/localstack/init/ready.d/init-bucket.sh

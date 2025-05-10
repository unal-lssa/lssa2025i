import os
import shutil


def generate_bucket(name: str, output_dir="skeleton"):
    path = f"{output_dir}/{name}"
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, "init-bucket.sh"), "w") as f:
        f.write("#!/bin/bash\n")
        f.write("set -e\n")
        f.write("\n")
        f.write("awslocal s3 mb s3://music-storage\n")
        f.write("awslocal s3 cp /songs/song.mp3 s3://music-storage/song.mp3")

    with open(os.path.join(path, "Dockerfile"), "w") as f:
        f.write("FROM localstack/localstack:s3-latest\n")
        f.write("RUN apt-get update && \\\n")
        f.write("    apt-get install -y python3-pip curl && \\\n")
        f.write("    pip3 install awscli awscli-local\n")
        f.write("\n")
        f.write("COPY init-bucket.sh /etc/localstack/init/ready.d/init-bucket.sh\n")
        f.write("COPY ./song.mp3 /songs/\n")
        f.write("RUN chmod +x /etc/localstack/init/ready.d/init-bucket.sh\n")


def move_file(src, dest):
    os.makedirs(dest, exist_ok=True)
    shutil.copy(src, os.path.join(dest, os.path.basename(src)))

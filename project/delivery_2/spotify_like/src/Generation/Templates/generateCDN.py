import os


def generate_cdn(name, output_dir="skeleton"):
    path = f"{output_dir}/{name}"
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, "nginx.conf"), "w") as f:
        f.write("worker_processes auto;\n")
        f.write("\n")
        f.write("events {\n")
        f.write("    worker_connections 1024;\n")
        f.write("}\n")
        f.write("\n")
        f.write("http {\n")
        f.write(
            "    proxy_cache_path /tmp/nginx_cache levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=24h use_temp_path=off;\n"
        )
        f.write("\n")
        f.write("    server {\n")
        f.write("        listen 80;\n")
        f.write("        server_name localhost;\n")
        f.write("\n")
        f.write("        location / {\n")
        f.write("            proxy_pass http://music_storage:4566;\n")
        f.write("            proxy_set_header Host $host;\n")
        f.write("            proxy_set_header X-Real-IP $remote_addr;\n")
        f.write(
            "            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        )
        f.write("            proxy_cache my_cache;\n")
        f.write("            proxy_cache_valid 200 1d;\n")
        f.write("            proxy_cache_use_stale error timeout updating;\n")
        f.write("        }\n")
        f.write("    }\n")
        f.write("}\n")

    with open(os.path.join(path, "Dockerfile"), "w") as f:
        f.write("FROM nginx:alpine\n")
        f.write("COPY nginx.conf /etc/nginx/nginx.conf\n")
        f.write('CMD ["nginx", "-g", "daemon off;"]\n')

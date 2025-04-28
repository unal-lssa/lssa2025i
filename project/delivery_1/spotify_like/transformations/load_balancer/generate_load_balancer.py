import os, textwrap

def generate_loadbalancer(name, service_name, instance_count):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    upstream_block = '\n'.join([f"        server {service_name}_{i}:80;" for i in range(instance_count)])

    nginx_conf = textwrap.dedent(f"""
        events {{}}

        http {{
            upstream servers {{
{upstream_block}
            }}

            server {{
                listen 80;

                location / {{
                    proxy_pass http://servers;
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
                }}
            }}
        }}
    """)

    with open(os.path.join(path, 'nginx.conf'), 'w') as f:
        f.write(nginx_conf)

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM nginx:alpine
            COPY nginx.conf /etc/nginx/nginx.conf
            
            EXPOSE 80
            
            CMD ["nginx", "-g", "daemon off;"]
        """))
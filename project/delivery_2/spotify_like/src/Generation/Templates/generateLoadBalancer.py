import os, textwrap
from DSL.AComponent import AComponent
from Generation.NetworkOrchestrator import NetworkOrchestrator


def generate_load_balancer(
    load_balancer: AComponent,
    net_orch: NetworkOrchestrator,
    output_dir="skeleton",
):
    path = f"{output_dir}/{load_balancer.name}"
    os.makedirs(path, exist_ok=True)

    upstream_block = "\n".join(
        [
            f"        server {target.name}:{net_orch.get_assigned_port(target)};"
            for target in load_balancer.targets
        ]
    )

    nginx_conf = textwrap.dedent(
        f"""
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
    """
    )

    with open(os.path.join(path, "nginx.conf"), "w") as f:
        f.write(nginx_conf)

    with open(os.path.join(path, "Dockerfile"), "w") as f:
        f.write(
            textwrap.dedent(
                """
            FROM nginx:alpine
            COPY nginx.conf /etc/nginx/nginx.conf

            EXPOSE 80

            CMD ["nginx", "-g", "daemon off;"]
        """
            )
        )

from transformations.templates import generate_templated_component


def generate_frontend(name, api_gateway, real_time_service):
    generate_templated_component(
        name,
        "frontend",
        {"api_gateway": api_gateway, "real_time_service": real_time_service},
    )

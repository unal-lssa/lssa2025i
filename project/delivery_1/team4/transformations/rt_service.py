from transformations.templates import generate_templated_component


def generate_real_time_service(name):
    generate_templated_component(
        name,
        "real-time-service",
    )

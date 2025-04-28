from transformations.templates import generate_templated_component


def generate_broker(name):
    generate_templated_component(
        name,
        "broker",
    )

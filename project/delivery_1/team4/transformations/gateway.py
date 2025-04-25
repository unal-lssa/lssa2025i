def generate_gateway(name, model):
    services = {}
    print("gateway name:", name)

    for e in model.elements:
        if e.__class__.__name__ == "Connector":
            print("Connector: ", "from ", e.from_, "to ", e.to_)

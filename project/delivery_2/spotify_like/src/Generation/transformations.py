import sys, os
from copy import deepcopy

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from DSL.AComponent import AComponent
from DSL.ApiGateway import ApiGateway
from DSL.Connector import Connector, ConnectorType
from DSL.Database import Database, DatabaseType
from DSL.IElement import IElement
from DSL.IVisitor import IVisitor
from DSL.LoadBalancer import LoadBalancer
from DSL.Model import Model
from DSL.Network import Network
from DSL.Queue import Queue
from DSL.StandardComponent import StandardComponent, StandardComponentType

# Change the visitor to change the deployment model logic
from Generation.DockerComposeWriterVisitor import DockerComposeWriterVisitor
from Generation.CodeGeneratorVisitor import CodeGeneratorVisitor


def convert_textx_to_dsl_element(elem) -> IElement:
    """
    Converts a TextX element to a DSL element.
    """
    cls_name = elem.__class__.__name__
    if cls_name == "Network":
        return Network(
            name=elem.name,
            internal=getattr(elem, "internal", False),
            driver=getattr(elem, "driver", None),
        )
    if cls_name == "StandardComponent":
        comp_type = StandardComponentType(elem.type)
        network = convert_textx_to_dsl_element(elem.network)
        return StandardComponent(name=elem.name, comp_type=comp_type, network=network)
    if cls_name == "Database":
        db_type = DatabaseType(elem.databaseType)
        network = convert_textx_to_dsl_element(elem.network)
        return Database(name=elem.name, database_type=db_type, network=network)
    if cls_name == "LoadBalancer":
        # target is a reference to another TextX component
        target = convert_textx_to_dsl_element(elem.target)
        network = convert_textx_to_dsl_element(elem.network)
        return LoadBalancer(
            name=elem.name,
            instance_count=elem.instanceCount,
            target=target,
            network=network,
        )
    if cls_name == "ApiGateway":
        auth = convert_textx_to_dsl_element(elem.auth)
        networks = [convert_textx_to_dsl_element(n) for n in elem.networks]
        return ApiGateway(name=elem.name, auth=auth, networks=networks)
    if cls_name == "Queue":
        network = convert_textx_to_dsl_element(elem.network)
        return Queue(
            name=elem.name,
            network=network,
        )
    if cls_name == "Connector":
        source = convert_textx_to_dsl_element(
            getattr(elem, "from", None)
        )  # 'from' is a reserved keyword
        target = convert_textx_to_dsl_element(elem.to)
        conn_type = ConnectorType(elem.type)
        return Connector(from_comp=source, to_comp=target, conn_type=conn_type)
    raise ValueError(f"Unsupported element type: {cls_name}")


def expand_load_balancer_instances(model: Model) -> Model:
    """
    Expands the load balancer instances in the model.
    """
    new_elements = []
    replicated_map = {}

    # Connectors are not expanded, but they are added to the new elements list
    components_to_update_map = {}

    for elem in model.elements:
        if not isinstance(elem, LoadBalancer) or elem.instance_count <= 1:
            new_elements.append(elem)
            continue

        # WARNING: Unlike if you are modifying targets somewhere else. Targets must be a list with a single element.
        if (len(elem.targets) > 1) and (new_name in replicated_map):
            raise RuntimeError(
                "The defined grammar does not allow the existence of a list of targets related to a loadbalancer. If you are seeing this error it is most likely that the architecture is being expanded more than 1 time (this method is being called more than 1 time)."
            )

        # Create multiple instances of the load balancer target
        replicas = list(elem.targets)
        for i in range(elem.instance_count - 1):
            suffix = f"_{i + 1}" if elem.instance_count > 0 else ""
            new_name = f"{elem.targets[0].name}{suffix}"

            clone = deepcopy(
                elem.targets[0]
            )  # Targets is defined as a single-item list BEFORE expansion.
            clone.name = new_name

            new_elements.append(clone)
            replicas.append(clone)

        # Update the connector references to point to the new instances
        components_to_update_map[replicas[0].name] = replicas[1:]

        lb_clone = deepcopy(elem)
        lb_clone.targets = replicas
        new_elements.append(lb_clone)
        replicated_map[elem] = replicas

    # Update the connectors to point to the new instances
    for elem in model.elements:
        if not isinstance(elem, Connector):
            continue

        # lb -> replica
        if elem.to_comp.name in components_to_update_map.keys():
            for replica in components_to_update_map[elem.to_comp.name]:
                new_conn = deepcopy(elem)
                new_conn.to_comp = replica
                new_conn.from_comp = elem.from_comp
                new_elements.append(new_conn)
        # replica -> other service
        elif elem.from_comp.name in components_to_update_map.keys():
            for replica in components_to_update_map[elem.from_comp.name]:
                new_conn = deepcopy(elem)
                new_conn.to_comp = elem.to_comp
                new_conn.from_comp = replica
                new_elements.append(new_conn)

    return Model(elements=new_elements)


def generate_architecture(model, output_dir: str = "skeleton"):
    converted_elems = []
    textx_to_domain_map = {}

    # First create all network elements to resolve references
    for elem in model.elements:
        if elem.__class__.__name__ == "Network":
            net = convert_textx_to_dsl_element(elem)
            textx_to_domain_map[elem] = net
            converted_elems.append(net)

    # Then create all other elements (except Connectors), using the network elements created above
    for elem in model.elements:
        if (
            elem.__class__.__name__ != "Network"
            and elem.__class__.__name__ != "Connector"
        ):
            inst = convert_textx_to_dsl_element(elem)
            textx_to_domain_map[elem] = inst
            converted_elems.append(inst)

    # Finally create all Connector elements, using the network and other elements created above
    for elem in model.elements:
        if elem.__class__.__name__ == "Connector":
            conn = convert_textx_to_dsl_element(elem)
            textx_to_domain_map[elem] = conn
            converted_elems.append(conn)

    # Validate the architecture
    base_arch = Model(
        elements=converted_elems,
    )
    arch = expand_load_balancer_instances(base_arch)
    arch.validate()

    # Use the visitor to generate the architecture
    code_visitor = CodeGeneratorVisitor(output_dir)
    docker_visitor = DockerComposeWriterVisitor(
        output_dir, network_orchestrator=code_visitor.network_orchestrator
    )  # Use the same port as the code generator
    arch.accept(code_visitor)
    arch.accept(docker_visitor)

import sys, os

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
            partitions=elem.partitions,
            replication=elem.replication,
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
    arch = Model(
        elements=converted_elems,
    )
    arch.validate()

    # Use the visitor to generate the architecture
    code_visitor = CodeGeneratorVisitor(output_dir)
    # docker_visitor = DockerComposeWriterVisitor(output_dir, network_orchestrator=code_visitor.network_orchestrator)  # Use the same port as the code generator
    arch.accept(code_visitor)
    # arch.accept(docker_visitor)

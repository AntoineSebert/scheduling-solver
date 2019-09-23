import xml.etree.ElementTree as ET


# Get nodes and edges from tsk file
# nodes: [id][attrib] = value
# edges: [{index}][attrib] = value
def read_tsk(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    nodes = {}
    edges = []
    for graph_child in root[0]:

        # Get nodes
        if graph_child.tag == 'Node':
            node_id = graph_child.attrib['Id']
            nodes[node_id] = {}
            for attrib in graph_child.attrib:
                nodes[node_id][attrib] = graph_child.attrib[attrib]

        # Get edges
        elif graph_child.tag == 'TaskGraph':
            for edge in graph_child:
                temp_edge = {}
                for attrib in edge.attrib:
                    temp_edge[attrib] = edge.attrib[attrib]
                edges.append(temp_edge)
    return {'nodes': nodes, 'edges': edges}


def read_cfg(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    cpus = {}
    for graph_child in root:

        # Get cpus
        if graph_child.tag == 'Cpu':
            cpu_id = graph_child.attrib['Id']
            cpus[cpu_id] = []
            for core in graph_child:
                if core.tag == 'Core':
                    cpus[cpu_id].append(core.attrib['Id'])
    return cpus


# Print nodes and edges
def print_case(graph, cpus):

    # Print nodes
    for node_id in graph['nodes']:
        print(F"Node {node_id}")
        for attrib in graph['nodes'][node_id]:
            print(F"\t{attrib}: {graph['nodes'][node_id][attrib]}")

    # Print edges
    print("Edges: Source -> Dest : Cost")
    for edge in graph['edges']:
        print(F"\t{edge['Source']} -> {edge['Dest']} : {edge['Cost']}")

    # Print cpus
    for cpu in cpus:
        print(F"CPU {cpu}")
        for core in cpus[cpu]:
            print(F"\tCore {core}")


print_case(read_tsk('cases/Case1.tsk'), read_cfg('cases/Case1.cfg'))
print("finished")

import xml.etree.ElementTree as ET


# Get nodes and edges from tsk file
# nodes: [id][attrib] = value
# edges_ftb: [source][dest] = value
# edges_btf: [dest][source] = value
def read_tsk(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    nodes = {}
    edges_ftb = {}
    edges_btf = {}
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
                source = edge.attrib['Source']
                dest = edge.attrib['Dest']

                if source not in edges_ftb.keys():
                    edges_ftb[source] = {}
                if dest not in edges_btf.keys():
                    edges_btf[dest] = {}

                edges_ftb[source][dest] = edge.attrib['Cost']
                edges_btf[dest][source] = edge.attrib['Cost']

    return {'nodes': nodes, 'edges_ftb': edges_ftb, 'edges_btf': edges_btf}


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

    # Print edges_ftb
    print("Edges_ftb: Source -> Dest : Cost")
    for source in graph['edges_ftb']:
        for dest in graph['edges_ftb'][source]:
            print(F"\t{source} -> {dest} : {graph['edges_ftb'][source][dest]}")

    # Print edges_btf
    print("Edges_btf: Dest -> Source : Cost")
    for dest in graph['edges_btf']:
        for source in graph['edges_btf'][dest]:
            print(F"\t{dest} -> {source} : {graph['edges_btf'][dest][source]}")
    # Print cpus
    for cpu in cpus:
        print(F"CPU {cpu}")
        for core in cpus[cpu]:
            print(F"\tCore {core}")


print_case(read_tsk('cases/Case1.tsk'), read_cfg('cases/Case1.cfg'))
print("finished")

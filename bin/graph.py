import os
import json
import re
import matplotlib.pyplot as plt
import networkx as nx
from jinja2 import Template

# Custom XML parser function provided by you
def xml(xml_string):
    # Load variables.json from the root directory (one level up)
    with open('../variables.json') as f:
        variables = json.load(f)
    
    # Render the XML string using Jinja templating
    template = Template(xml_string)
    xml_string = template.render(variables)

    # Regular expression patterns to match different elements
    tag_pattern = re.compile(r'<(?P<tag>[a-z]+) (?P<attributes>[^>]+)>(?P<content>.*?)</\1>', re.DOTALL)
    attr_pattern = re.compile(r'(?P<key>[a-z_]+)="(?P<value>[^"]*)"')

    elements_list = []

    # Find all tags with their attributes and content
    for match in tag_pattern.finditer(xml_string):
        tag_dict = {}
        # Extract the tag name, attributes, and inner content
        tag = match.group('tag')
        attributes = match.group('attributes')
        content = match.group('content').strip()

        # Parse attributes
        for attr_match in attr_pattern.finditer(attributes):
            key = attr_match.group('key')
            value = attr_match.group('value')
            tag_dict[key] = value

        # Add the content as 'code'
        tag_dict['code'] = content

        # Add the tag name as 'type'
        tag_dict['type'] = tag

        # Append the tag dictionary to the list
        elements_list.append(tag_dict)

    return elements_list

# Parser to read XML file and apply the custom xml function
def parser(xml_file_path):
    # Open and read the file content into a string
    with open(xml_file_path, 'r') as file:
        xml_string = file.read()

    # Parse the XML string using the custom XML function
    elements_list = xml(xml_string)

    # Output the result
    return elements_list

# Function to create a graph traversal order and output as graph.json and graph.png
def create_pipeline_json_and_graph(pipelines_folder='../pipelines/'):
    graph_data = {}

    # Iterate through all .xml files in the pipelines directory
    for filename in os.listdir(pipelines_folder):
        if filename.endswith(".xml"):
            file_path = os.path.join(pipelines_folder, filename)
            print(f"Parsing file: {file_path}")  # Debug output

            # Use the custom parser function instead of xml.etree.ElementTree
            try:
                elements = parser(file_path)

                # Traverse each parsed element and collect input-output relationships
                for element in elements:
                    elem_id = element.get('id')
                    elem_type = element.get('type')

                    # Only focus on python and sql components for the graph model
                    if elem_type in ['python', 'sql']:
                        graph_data[elem_id] = {
                            'type': elem_type,
                            'inputs': element.get('inputs', '').split(",") if element.get('inputs') else [],
                            'outputs': [],  # To be filled when traversing other elements
                            'chains_to': None  # Check if it chains to another pipeline
                        }

                        # Check for pipeline chaining (e.g., in Python code)
                        if elem_type == 'python' and 'Pipeline(' in element['code']:
                            chain_match = re.search(r'Pipeline\([\'"](.*?\.xml)[\'"]\)', element['code'])
                            if chain_match:
                                graph_data[elem_id]['chains_to'] = chain_match.group(1)

            except Exception as e:
                print(f"Error parsing file {file_path}: {e}")
                continue  # Skip to the next file if parsing fails

    # Now that we have collected all elements, let's build output dependencies
    for elem_id, elem_data in graph_data.items():
        for input_id in elem_data['inputs']:
            if input_id and input_id in graph_data:
                graph_data[input_id]['outputs'].append(elem_id)

    # Write the graph data to a JSON file
    with open('../graph.json', 'w') as json_file:
        json.dump(graph_data, json_file, indent=4)

    print("graph.json created successfully!")

    # Now generate the graph image and save as graph.png
    generate_pipeline_graph(graph_data, '../graph.png')
    print("graph.png created successfully!")

def generate_pipeline_graph(data, output_filename):
    """
    Function to generate a pipeline graph from JSON data and save it as a .png file.
    
    Args:
    data (dict): JSON data describing the pipeline with tasks and their connections.
    output_filename (str): Name of the file where the graph will be saved.
    
    Returns:
    None
    """
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges based on the JSON data
    for task, info in data.items():
        G.add_node(task, type=info['type'])
        for output in info['outputs']:
            G.add_edge(task, output)

    # Assign colors based on type (python or sql)
    color_map = []
    for node in G:
        if G.nodes[node]['type'] == 'python':
            color_map.append('#93c9a2')
        else:
            color_map.append('#5177b0')

    # Custom linear layout: spread nodes horizontally by their shell layers
    def linear_layout(shell_layers):
        pos = {}
        x_offset = 0  # Control the horizontal distance between layers
        y_offset = 0
        layer_spacing = 10  # Adjust horizontal spacing between layers
        node_spacing = 5   # Adjust vertical spacing within the same layer (now vertical)

        for i, layer in enumerate(shell_layers):
            # Place nodes vertically spaced within each layer
            for j, node in enumerate(layer):
                pos[node] = (i * layer_spacing, -j * node_spacing)  # Left to right layout
        return pos

    # Use the shell layers (generated in your existing code) and apply the linear layout
    layers = {}
    def get_depth(node, current_depth=0):
        if node not in layers or current_depth > layers[node]:
            layers[node] = current_depth
        for neighbor in G.successors(node):
            get_depth(neighbor, current_depth + 1)

    # Initialize depths
    for node in G:
        if not list(G.predecessors(node)):  # Starting nodes (no inputs)
            get_depth(node)

    # Group nodes by depth
    shell_layers = [[] for _ in range(max(layers.values()) + 1)]
    for node, depth in layers.items():
        shell_layers[depth].append(node)
    

    # Use custom linear layout
    pos = linear_layout(shell_layers)

    # Draw the graph
    plt.figure(figsize=(1.4 * len(data), 1.2 * len(data)))
    nx.draw(G, pos, arrowsize=22, with_labels=True, node_color=color_map, node_size=15000,
            font_weight='bold', font_size=11, font_color='white', arrows=True, node_shape='o',verticalalignment='center_baseline')
    plt.title('Task Flow Graph (Left to Right Layout)')

    # Save the graph as a .png file
    plt.savefig(output_filename)
    plt.close()
create_pipeline_json_and_graph()








### OLD VERSION -- TOP TO BOTTOM
# import os
# import json
# import re
# import matplotlib.pyplot as plt
# import networkx as nx
# from jinja2 import Template

# # Custom XML parser function provided by you
# def xml(xml_string):
#     # Load variables.json from the root directory (one level up)
#     with open('../variables.json') as f:
#         variables = json.load(f)
    
#     # Render the XML string using Jinja templating
#     template = Template(xml_string)
#     xml_string = template.render(variables)

#     # Regular expression patterns to match different elements
#     tag_pattern = re.compile(r'<(?P<tag>[a-z]+) (?P<attributes>[^>]+)>(?P<content>.*?)</\1>', re.DOTALL)
#     attr_pattern = re.compile(r'(?P<key>[a-z_]+)="(?P<value>[^"]*)"')

#     elements_list = []

#     # Find all tags with their attributes and content
#     for match in tag_pattern.finditer(xml_string):
#         tag_dict = {}
#         # Extract the tag name, attributes, and inner content
#         tag = match.group('tag')
#         attributes = match.group('attributes')
#         content = match.group('content').strip()

#         # Parse attributes
#         for attr_match in attr_pattern.finditer(attributes):
#             key = attr_match.group('key')
#             value = attr_match.group('value')
#             tag_dict[key] = value

#         # Add the content as 'code'
#         tag_dict['code'] = content

#         # Add the tag name as 'type'
#         tag_dict['type'] = tag

#         # Append the tag dictionary to the list
#         elements_list.append(tag_dict)

#     return elements_list

# # Parser to read XML file and apply the custom xml function
# def parser(xml_file_path):
#     # Open and read the file content into a string
#     with open(xml_file_path, 'r') as file:
#         xml_string = file.read()

#     # Parse the XML string using the custom XML function
#     elements_list = xml(xml_string)

#     # Output the result
#     return elements_list

# # Function to create a graph traversal order and output as graph.json and graph.png
# def create_pipeline_json_and_graph(pipelines_folder='../pipelines/'):
#     graph_data = {}

#     # Iterate through all .xml files in the pipelines directory
#     for filename in os.listdir(pipelines_folder):
#         if filename.endswith(".xml"):
#             file_path = os.path.join(pipelines_folder, filename)
#             print(f"Parsing file: {file_path}")  # Debug output

#             # Use the custom parser function instead of xml.etree.ElementTree
#             try:
#                 elements = parser(file_path)

#                 # Traverse each parsed element and collect input-output relationships
#                 for element in elements:
#                     elem_id = element.get('id')
#                     elem_type = element.get('type')

#                     # Only focus on python and sql components for the graph model
#                     if elem_type in ['python', 'sql']:
#                         graph_data[elem_id] = {
#                             'type': elem_type,
#                             'inputs': element.get('inputs', '').split(",") if element.get('inputs') else [],
#                             'outputs': [],  # To be filled when traversing other elements
#                             'chains_to': None  # Check if it chains to another pipeline
#                         }

#                         # Check for pipeline chaining (e.g., in Python code)
#                         if elem_type == 'python' and 'Pipeline(' in element['code']:
#                             chain_match = re.search(r'Pipeline\([\'"](.*?\.xml)[\'"]\)', element['code'])
#                             if chain_match:
#                                 graph_data[elem_id]['chains_to'] = chain_match.group(1)

#             except Exception as e:
#                 print(f"Error parsing file {file_path}: {e}")
#                 continue  # Skip to the next file if parsing fails

#     # Now that we have collected all elements, let's build output dependencies
#     for elem_id, elem_data in graph_data.items():
#         for input_id in elem_data['inputs']:
#             if input_id and input_id in graph_data:
#                 graph_data[input_id]['outputs'].append(elem_id)

#     # Write the graph data to a JSON file
#     with open('../graph.json', 'w') as json_file:
#         json.dump(graph_data, json_file, indent=4)

#     print("graph.json created successfully!")

#     # Now generate the graph image and save as graph.png
#     generate_pipeline_graph(graph_data, '../graph.png')
#     print("graph.png created successfully!")

# def generate_pipeline_graph(data, output_filename):
#     """
#     Function to generate a pipeline graph from JSON data and save it as a .png file.
    
#     Args:
#     data (dict): JSON data describing the pipeline with tasks and their connections.
#     output_filename (str): Name of the file where the graph will be saved.
    
#     Returns:
#     None
#     """
#     # Create a directed graph
#     G = nx.DiGraph()

#     # Add nodes and edges based on the JSON data
#     for task, info in data.items():
#         G.add_node(task, type=info['type'])
#         for output in info['outputs']:
#             G.add_edge(task, output)

#     # Assign colors based on type (python or sql)
#     color_map = []
#     for node in G:
#         if G.nodes[node]['type'] == 'python':
#             color_map.append('#93c9a2')
#         else:
#             color_map.append('#5177b0')

#     # Custom linear layout: spread nodes horizontally by their shell layers
#     def linear_layout(shell_layers):
#         pos = {}
#         x_offset = 0  # Control the horizontal distance between layers
#         y_offset = 0
#         layer_spacing = 5  # Adjust vertical spacing between layers
#         node_spacing = 10  # Adjust horizontal spacing within the same layer

#         for i, layer in enumerate(shell_layers):
#             # Place nodes horizontally spaced within each layer
#             for j, node in enumerate(layer):
#                 pos[node] = (j * node_spacing, -i * layer_spacing)  # Horizontal layout with vertical layers
#         return pos

#     # Use the shell layers (generated in your existing code) and apply the linear layout
#     layers = {}
#     def get_depth(node, current_depth=0):
#         if node not in layers or current_depth > layers[node]:
#             layers[node] = current_depth
#         for neighbor in G.successors(node):
#             get_depth(neighbor, current_depth + 1)

#     # Initialize depths
#     for node in G:
#         if not list(G.predecessors(node)):  # Starting nodes (no inputs)
#             get_depth(node)

#     # Group nodes by depth
#     shell_layers = [[] for _ in range(max(layers.values()) + 1)]
#     for node, depth in layers.items():
#         shell_layers[depth].append(node)

#     # Use custom linear layout
#     pos = linear_layout(shell_layers)

#     # Draw the graph
#     plt.figure(figsize=(1.4 * len(data), 1.2 * len(data)))
#     nx.draw(G, pos, arrowsize=20, with_labels=True, node_color=color_map, node_size=7000,
#             font_weight='bold', font_size=10, font_color='white', arrows=True, node_shape='o')
#     plt.title('Task Flow Graph (Linear Layout)')

#     # Save the graph as a .png file
#     plt.savefig(output_filename)
#     plt.close()

# Call the function to create and save the pipeline traversal order to graph.json and graph.png
# create_pipeline_json_and_graph()














### OLD VERSION -- NO FLOW CONTROL

# import os
# import json
# import re
# import matplotlib.pyplot as plt
# import networkx as nx
# from jinja2 import Template

# # Custom XML parser function provided by you
# def xml(xml_string):
#     # Load variables.json from the root directory (one level up)
#     with open('../variables.json') as f:
#         variables = json.load(f)
    
#     # Render the XML string using Jinja templating
#     template = Template(xml_string)
#     xml_string = template.render(variables)

#     # Regular expression patterns to match different elements
#     tag_pattern = re.compile(r'<(?P<tag>[a-z]+) (?P<attributes>[^>]+)>(?P<content>.*?)</\1>', re.DOTALL)
#     attr_pattern = re.compile(r'(?P<key>[a-z_]+)="(?P<value>[^"]*)"')

#     elements_list = []

#     # Find all tags with their attributes and content
#     for match in tag_pattern.finditer(xml_string):
#         tag_dict = {}
#         # Extract the tag name, attributes, and inner content
#         tag = match.group('tag')
#         attributes = match.group('attributes')
#         content = match.group('content').strip()

#         # Parse attributes
#         for attr_match in attr_pattern.finditer(attributes):
#             key = attr_match.group('key')
#             value = attr_match.group('value')
#             tag_dict[key] = value

#         # Add the content as 'code'
#         tag_dict['code'] = content

#         # Add the tag name as 'type'
#         tag_dict['type'] = tag

#         # Append the tag dictionary to the list
#         elements_list.append(tag_dict)

#     return elements_list

# # Parser to read XML file and apply the custom xml function
# def parser(xml_file_path):
#     # Open and read the file content into a string
#     with open(xml_file_path, 'r') as file:
#         xml_string = file.read()

#     # Parse the XML string using the custom XML function
#     elements_list = xml(xml_string)

#     # Output the result
#     return elements_list

# # Function to create a graph traversal order and output as graph.json and graph.png
# def create_pipeline_json_and_graph(pipelines_folder='../pipelines/'):
#     graph_data = {}

#     # Iterate through all .xml files in the pipelines directory
#     for filename in os.listdir(pipelines_folder):
#         if filename.endswith(".xml"):
#             file_path = os.path.join(pipelines_folder, filename)
#             print(f"Parsing file: {file_path}")  # Debug output

#             # Use the custom parser function instead of xml.etree.ElementTree
#             try:
#                 elements = parser(file_path)

#                 # Traverse each parsed element and collect input-output relationships
#                 for element in elements:
#                     elem_id = element.get('id')
#                     elem_type = element.get('type')

#                     # Only focus on python and sql components for the graph model
#                     if elem_type in ['python', 'sql']:
#                         graph_data[elem_id] = {
#                             'type': elem_type,
#                             'inputs': element.get('inputs', '').split(",") if element.get('inputs') else [],
#                             'outputs': [],  # To be filled when traversing other elements
#                             'chains_to': None  # Check if it chains to another pipeline
#                         }

#                         # Check for pipeline chaining (e.g., in Python code)
#                         if elem_type == 'python' and 'Pipeline(' in element['code']:
#                             chain_match = re.search(r'Pipeline\([\'"](.*?\.xml)[\'"]\)', element['code'])
#                             if chain_match:
#                                 graph_data[elem_id]['chains_to'] = chain_match.group(1)

#             except Exception as e:
#                 print(f"Error parsing file {file_path}: {e}")
#                 continue  # Skip to the next file if parsing fails

#     # Now that we have collected all elements, let's build output dependencies
#     for elem_id, elem_data in graph_data.items():
#         for input_id in elem_data['inputs']:
#             if input_id and input_id in graph_data:
#                 graph_data[input_id]['outputs'].append(elem_id)

#     # Write the graph data to a JSON file
#     with open('../graph.json', 'w') as json_file:
#         json.dump(graph_data, json_file, indent=4)

#     print("graph.json created successfully!")

#     # Now generate the graph image and save as graph.png
#     generate_pipeline_graph(graph_data, '../graph.png')
#     print("graph.png created successfully!")

# # Function to generate the pipeline graph and save it as a PNG
# def generate_pipeline_graph(data, output_filename):
#     """
#     Function to generate a pipeline graph from JSON data and save it as a .png file.
    
#     Args:
#     data (dict): JSON data describing the pipeline with tasks and their connections.
#     output_filename (str): Name of the file where the graph will be saved.
    
#     Returns:
#     None
#     """
#     # Create a directed graph
#     G = nx.DiGraph()

#     # Add nodes and edges based on the JSON data
#     for task, info in data.items():
#         G.add_node(task, type=info['type'])
#         for output in info['outputs']:
#             G.add_edge(task, output)

#     # Assign colors based on type (python or sql)
#     color_map = []
#     for node in G:
#         if G.nodes[node]['type'] == 'python':
#             color_map.append('#93c9a2')
#         else:
#             color_map.append('#5177b0')

#     # Use shell layout for consistent, structured node placement
#     # Automatically generate shells by grouping nodes based on depth in the graph
#     layers = {}
#     def get_depth(node, current_depth=0):
#         if node not in layers or current_depth > layers[node]:
#             layers[node] = current_depth
#         for neighbor in G.successors(node):
#             get_depth(neighbor, current_depth + 1)

#     # Initialize depths
#     for node in G:
#         if not list(G.predecessors(node)):  # Starting nodes (no inputs)
#             get_depth(node)

#     # Group nodes by depth
#     shell_layers = [[] for _ in range(max(layers.values()) + 1)]
#     for node, depth in layers.items():
#         shell_layers[depth].append(node)

#     pos = nx.shell_layout(G, nlist=shell_layers)  # Generate shell layout positions

#     # Draw the graph
#     plt.figure(figsize=(1.4*len(data), 1.2*len(data) ))
#     nx.draw(G, pos, arrowsize=20, with_labels=True, node_color=color_map, node_size=7000, font_weight='bold', font_size=10, font_color='white', arrows=True,node_shape='o')
#     plt.title('Task Flow Graph (Generated)')
    
#     # Save the graph as a .png file
#     plt.savefig(output_filename)
#     plt.close()

# # Call the function to create and save the pipeline traversal order to graph.json and graph.png
# create_pipeline_json_and_graph()


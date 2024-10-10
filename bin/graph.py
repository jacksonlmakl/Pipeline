import os
import json
import re
from jinja2 import Template

# Custom XML parser function provided by you
def xml(xml_string):
    # Load your variables.json file
    with open('variables.json') as f:
        variables = json.load(f)
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

# Function to create a graph traversal order and output as graph.json
def create_pipeline_json(pipelines_folder='pipelines/'):
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
    with open('graph.json', 'w') as json_file:
        json.dump(graph_data, json_file, indent=4)

    print("graph.json created successfully!")

# Call the function to create and save the pipeline traversal order to graph.json
create_pipeline_json()

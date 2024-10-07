from core import Task
from core import Connection
from core import Table
import re
def xml(xml_string):
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


# Example usage
# Define the path to the XML file
def parser(xml_file_path):
    # Open and read the file content into a string
    with open(xml_file_path, 'r') as file:
        xml_string = file.read()
    
    # Parse the XML string
    elements_list = xml(xml_string)
    
    # Output the result
    data = []
    for element in elements_list:
        data.append(element)
    return data



#Parse & Load raw data 
class Pipeline:
    def __init__(self, file):
        data=parser(file)
        connections_raw=[i for i in data if i['type']=='connection']
        tasks_raw=[i for i in data if i['type']=='task']
        table_raw=[i for i in data if i['type']=='sql' or i['type']=='python']
        self.tasks=[Task(task['id'],
        task['schedule'],
        task['active'],
        task['steps'],
        task['force_build'],
        task['code'],
        task['type']) for task in tasks_raw]
        
        self.connections=[Connection(id=connection['id'],
        host=connection['host'],
        port=connection['port'],
        username=connection['username'],
        password=connection['password']) for connection in connections_raw]
        
        self.tables=[Table(table.get('id',''),
            table.get('table',''),
            table.get('schema',''),
            table.get('database',''),
            table.get('connection',''),
            table.get('materialization',''),
            table.get('primary_key',''),
            table.get('inputs',''),
            table.get('schema_change',''),
            table.get('code',''),
            table.get('type','')) for table in table_raw]
        





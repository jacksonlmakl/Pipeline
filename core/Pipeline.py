from core import Task, Connection, Table
import re
import yaml
from jinja2 import Template

# Load Jinja variables from the YAML file
def load_yaml_variables(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        variables = yaml.safe_load(file)
    return variables

# Parse XML with Jinja rendering
def xml(xml_string, variables):
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

        # Render content using Jinja2 if there are any Jinja templates
        template = Template(content)
        rendered_content = template.render(variables)
        tag_dict['code'] = rendered_content  # Store the rendered content as 'code'

        # Add the tag name as 'type'
        tag_dict['type'] = tag

        # Append the tag dictionary to the list
        elements_list.append(tag_dict)

    return elements_list

# Example usage
def parser(xml_file_path):
    # Load variables from the YAML file
    variables = load_yaml_variables('variables.yml')

    # Open and read the XML file content into a string
    with open(xml_file_path, 'r') as file:
        xml_string = file.read()

    # Parse the XML string with Jinja rendering
    elements_list = xml(xml_string, variables)

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


        self.file_name=file
        self.connections=[Connection(id=connection['id'],
        host=connection['host'],
        port=connection['port'],
        username=connection['username'],
        password=connection['password'],
        database=connection['database']) for connection in connections_raw]
        
        self.tables=[Table(table.get('id',''),
            table.get('table',''),
            table.get('schema',''),
            table.get('database',''),
            [i for i in self.connections if i.id == table.get('connection','')],
            table.get('materialization',''),
            table.get('primary_key',''),
            table.get('inputs',''),
            table.get('schema_change',''),
            table.get('code',''),
            table.get('type',''),table.get('handler',''),self) for table in table_raw]
        
        self.tasks=[Task(task['id'],
        task['schedule'],
        task.get('active',''),
        [i for i in self.tables if i.id in task.get('steps',[])],
        task.get('force_build',''),
        task.get('code',''),
        task.get('type',''),self) for task in tasks_raw]
    def get_table(self,table_id):
        tbl=[i for i in self.tables if i.id==table_id]
        if len(tbl)==0:
            raise Exception("Table not found")
        else:
            return tbl[0]
    def run(self):
        for table in self.tables:
            print(f"Building Table '{table.id}' .....")
            self.get_table(table.id).build()
            print("Done.\n")
    def start(self):
        return self.tasks[0].start()





# from core import Task
# from core import Connection
# from core import Table
# import re
# def xml(xml_string):
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


# # Example usage
# # Define the path to the XML file
# def parser(xml_file_path):
#     # Open and read the file content into a string
#     with open(xml_file_path, 'r') as file:
#         xml_string = file.read()
    
#     # Parse the XML string
#     elements_list = xml(xml_string)
    
#     # Output the result
#     data = []
#     for element in elements_list:
#         data.append(element)
#     return data



#Parse & Load raw data 
class Pipeline:
    def __init__(self, file):
        data=parser(file)
        connections_raw=[i for i in data if i['type']=='connection']
        tasks_raw=[i for i in data if i['type']=='task']
        table_raw=[i for i in data if i['type']=='sql' or i['type']=='python']


        self.file_name=file
        self.connections=[Connection(id=connection['id'],
        host=connection['host'],
        port=connection['port'],
        username=connection['username'],
        password=connection['password'],
        database=connection['database']) for connection in connections_raw]
        
        self.tables=[Table(table.get('id',''),
            table.get('table',''),
            table.get('schema',''),
            table.get('database',''),
            [i for i in self.connections if i.id == table.get('connection','')],
            table.get('materialization',''),
            table.get('primary_key',''),
            table.get('inputs',''),
            table.get('schema_change',''),
            table.get('code',''),
            table.get('type',''),table.get('handler',''),self) for table in table_raw]
        
        self.tasks=[Task(task['id'],
        task['schedule'],
        task.get('active',''),
        [i for i in self.tables if i.id in task.get('steps',[])],
        task.get('force_build',''),
        task.get('code',''),
        task.get('type',''),self) for task in tasks_raw]
    def get_table(self,table_id):
        tbl=[i for i in self.tables if i.id==table_id]
        if len(tbl)==0:
            raise Exception("Table not found")
        else:
            return tbl[0]
    def run(self):
        for table in self.tables:
            print(f"Building Table '{table.id}' .....")
            self.get_table(table.id).build()
            print("Done.\n")
    def start(self):
        return self.tasks[0].start()





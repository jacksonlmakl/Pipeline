import os
import subprocess
import pandas

def run_python_code(code_str, file_name):
    # Step 1: Save the Python code string to a file
    with open(file_name, "w") as f:
        f.write(code_str)
    
    # Step 2: Check if virtual environment 'env' exists, if not, create it
    env_dir = os.path.join(os.getcwd(), 'env')
    if not os.path.exists(env_dir):
        print("Virtual environment 'env' not found. Creating it from requirements.txt...")
        subprocess.run(["python3", "-m", "venv", "env"])
        # Install dependencies from requirements.txt if it exists
        
        if os.path.exists("requirements.txt"):
            subprocess.run([os.path.join(env_dir, "bin", "pip"), "install", "-r", "requirements.txt"])
        else:
            print("No requirements.txt found. Virtual environment created without dependencies.")
    
    # Step 3: Activate the virtual environment and run the Python file
    activate_script = os.path.join(env_dir, "bin", "activate")
    python_exec = os.path.join(env_dir, "bin", "python")

    # Using bash -c to ensure that Ubuntu's shell handles 'source' correctly
    command = f"bash -c 'source {activate_script} && {python_exec} {file_name}'"

    # Step 4: Capture the output of running the Python file
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Step 5: Return the log of the run as a string
    return result.stdout



class Table:
    def __init__(self,id,table,schema,database,connection,materialization,primary_key,inputs,schema_change,code,type,handler=None,pipeline=None):
        self.id = id
        self.table = table
        self.schema = schema
        self.database = database
        self.connection = connection[0] if len(connection)>0 else None
        self.materialization = materialization if materialization else None
        self.handler = handler
        self.primary_key = primary_key if primary_key else None
        self.inputs = inputs if inputs else []
        self.schema_change = schema_change
        self.code = code
        self.type = type
        self.pipeline=pipeline
        self.validate()
    def validate(self):
        if self.materialization=='incremental' and self.primary_key==None:
            raise Exception("Incremental materialization requires a valid primary_key argument")
    def get_dataframe(self):
        self.connection.Session()
        try:
            df=self.connection.query_to_df(f""" SELECT * FROM "{self.schema}"."{self.table}" """)
        except Exception as E:
            df=None
            print(str(E))
            pass
        self.connection.close()
        return df
    def build(self):
        if self.materialization =="" or self.materialization==None:
            if self.type=='sql':
                self.connection.query(self.code)
                print(self.code)
                return self.code
        if self.materialization != "" and self.materialization != None and self.type!='python':
            df=self.get_dataframe()
        input_tables=[i for i in self.pipeline.tables if i.id in self.inputs]
        try:
            dne_inputs=[i.id for i in input_tables if type(i.get_dataframe()) == type(None)]
        except:
            input_tables=[]
            dne_inputs=[]
        if len(dne_inputs)>0:
            input_tables=[i for i in input_tables if i.id not in dne_inputs]
            if self.materialization != "" and self.materialization != None:
                raise Exception(f"The following inputs do not exist: {dne_inputs}")
        if self.materialization != "" and self.materialization != None and self.type!='python':
            self.connection.Session()
        if self.type=='python':
            input_str = '\n'.join([f"""{i.id} = [i.get_dataframe() for i in p.tables if i.id == '{i.id}'][0]""" for i in input_tables])
            formatted_code = f"""from core import Pipeline\n\n{self.code}\n\np=Pipeline('{self.pipeline.file_name}')\n\n{input_str}\n\n{self.id} = {self.handler}({','.join([i.id for i in input_tables])})"""
            if self.materialization != "" and self.materialization != None:
                formatted_code = formatted_code+f"""\n\ncurr_table=[i for i in p.tables if i.id=='{self.id}'][0]\n """ +f"""\n\n\n[i.connection for i in p.tables if i.id == '{self.id}'][0].Session()\n\ncurr_table.connection.df_to_table({self.id}, curr_table.table, curr_table.database, curr_table.schema, curr_table.materialization, schema_change_behavior=curr_table.schema_change, primary_key=curr_table.primary_key)"""
            r=run_python_code(formatted_code, f"compute__{self.id}.py")
            print(r)
            return r

        elif self.type=='sql':
            query=self.code
            print(query)
            self.connection.query_to_table(query, self.table, self.database, self.schema, self.materialization, schema_change_behavior=self.schema_change, primary_key=self.primary_key)

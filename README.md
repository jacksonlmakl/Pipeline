# Pipeline

## Requirements:
- Python 3.10.
- Unix-based operating system (e.g., Linux, macOS).
- Root access.
## Setup:
- ``git clone https://github.com/jacksonlmakl/Pipeline.git``
- ``cd Pipeline``.
- ``bin/setup``.


## Usage:
- Add Python requirements for your pipeline files in ``requirements.txt`` (Do not remove existing packages).
- Create new pipelines by adding .xml files to ``pipelines/`` (See ``sample.xml`` for formatting).
- Pipeline files support Jinja templating. You can store your variables in the ``variables.json`` configuration file.
- Start your pipeline files with the commands:
  	- ``cd Pipeline/`` (If this is not already your current directory).
	- ``pipeline <YOUR FILE NAME>``.
- Kill processes with the command:
	- ``bin/stop <YOUR FILE NAME>``.
 ## Example Usage:
 - Make sure ``kanto.xml`` & ``johto.xml`` exist in the ``pipelines/`` directory.
 - ``pipeline kanto`` (To start a scheduled pipeline).
 - The Kanto Pipeline will kick off. This runs an ETL Pipeline building tables on Pokemon from the Kanto region. It also kicks off ``johto.xml`` which runs a ETL Pipeline for tables on Pokemon in the Johto region.
 - ``bin/stop kanto`` (To stop a running/scheduled pipeline).


# **Pipeline XML Configuration Documentation**

## **Overview**

The `.xml` files within the ``pipelines/`` directory each define a complete data processing pipeline using XML. These files contain all necessary configuration details, including database connections, tasks (Python or SQL), and the workflow logic. The pipelines typically handle data extraction, transformation, and loading (ETL) across various stages of processing.

## **Structure**

The XML file contains several key elements:
- **Connection**: Defines a database or external system connection.
- **Task**: Specifies an individual task, either Python or SQL, that runs within the pipeline.
- **Python**: Executes a Python script.
- **SQL**: Executes an SQL query on the specified database.
- **Materialization**: Controls how tables are managed (e.g., truncating, incremental updates).

## **Important Features**
- **Jinja**: You may use Jinja when writing Pipeline files. Save variables to ``variables.json``.
- **Chaining Pipelines**: You can kick off another pipeline by creating a Python component and using the code:
	```python
	from core import Pipeline
	p=Pipeline('pipelines/johto.xml')
	p.run()
	```
  
  
## **Explanation of Key Components**

### **1. Connection**
```xml
<connection id="connection_1" host="{{ connection_1_host }}" port="{{ connection_1_port }}" username="{{ connection_1_username }}" database="{{ connection_1_database }}" password="{{ connection_1_password }}"></connection>
```
#### Note: The above example is templated using Jinja and the variables.json.

- **id**: Unique identifier for the connection.
- **host**: The host URL or IP address.
- **port**: Port number for the connection.
- **username**: Username to authenticate.
- **database**: Target database.
- **password**: Authentication password (use environment variables for security).

### **2. Task**
```xml
<task id="task_2" schedule="*/1 * * * *"></task>
```
#### Note: You may only have 1 task per Pipeline file.

- **id**: Unique identifier for the task.
- **schedule**: Cron-like schedule expression (e.g., every minute).

### **3. Python**
```xml
<python id="t5" table="JOHTO_LANDING" schema="POKEMON" database="RAW" handler="main" connection="connection_1" materialization="truncate" inputs="" schema_change="drop_and_recreate">
```
#### Note: Your Python component's handler must take in a table created by another component, or nothing at all. The handler must output a dataframe. 

- **id**: Unique object identifier.
- **table**: Target table name.
- **schema**: Schema of the target table.
- **database**: Database where the table resides.
- **handler**: Function in the script to execute (must match Python code).
- **connection**: Connection id to use.
- **materialization**: Determines how to handle the data (e.g., `truncate` to overwrite, `incremental` to insert/update on primary key column, 'temp' for temp table).
- **inputs**: Object id's of tables that are inputs to this processor. 
- **schema_change**: Handle schema changes (e.g., `drop_and_recreate`,`error`).

### **4. SQL**
```xml
<sql id="t7" table="JOHTO_RAW" schema="POKEMON" database="RAW" connection="connection_1" materialization="incremental" primary_key="name" inputs="t6" schema_change="drop_and_recreate">
```
- **id**: Unique object identifier.
- **table**: Target table.
- **schema**: Schema of the target table.
- **database**: Target database.
- **connection**: Database connection to use.
- **materialization**: Defines how the data should be written (e.g., `truncate` to overwrite, `incremental` to insert/update on primary key column, 'temp' for temp table).
- **inputs**: Object id's of tables that are inputs to this processor.
- **primary_key**: Column used to identify unique rows for incremental loads (Required for incremental materialization).
- **schema_change**: Handle schema changes (e.g., `drop_and_recreate`,`error`).
- 
## **Writing Python/SQL Code Inside XML**

- The Python/SQL code should be placed within a `python` or `sql` component.
  
Example:
```xml
# Your Python code goes here
def main():
    return get_johto_pokemon()
```

## **Final Remarks**

- Ensure the XML is well-formed with matching tags and properly escaped content.
- Schedule tasks carefully using cron syntax to avoid overlapping jobs.
- Utilize the `materialization` and `schema_change` attributes to control how data is loaded into tables, ensuring schema compatibility.

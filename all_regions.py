
from core import Pipeline

file_name = 'pipelines/'+'all_regions'+'.xml'
p = Pipeline(file_name)
print(f'Pipeline {file_name} Started.....')
p.start()


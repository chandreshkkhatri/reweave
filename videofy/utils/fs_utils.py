import json
from pathlib import Path


def write_script_to_file(content, filename, dirname):
    Path(dirname).mkdir(parents=True, exist_ok=True)
    with open(f'{dirname}/{filename}', 'w') as f:
        f.write(content)
        
        
def read_script_from_file(filename, dirname):
    with open(f'{dirname}/{filename}', 'r') as f:
        raw_content = f.read()
    
    return json.loads(raw_content)
    

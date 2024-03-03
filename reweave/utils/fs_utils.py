from pathlib import Path


def write_content_to_file(content, filename, dirname):
    Path(dirname).mkdir(parents=True, exist_ok=True)
    with open(f'{dirname}/{filename}', 'w') as f:
        f.write(content)
        
        
def write_bytes_to_file(content, filename, dirname):
    Path(dirname).mkdir(parents=True, exist_ok=True)
    Path(f'{dirname}/{filename}').write_bytes(content)
    
def write_stream_to_file(content, filename, dirname):
    Path(dirname).mkdir(parents=True, exist_ok=True)
    content.stream_to_file(f"{dirname}/{filename}")
        
def read_content_from_file(filename, dirname):
    with open(f'{dirname}/{filename}', 'r') as f:
        raw_content = f.read()
    
    return raw_content
    

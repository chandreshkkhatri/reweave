import os
import sys
import subprocess

# Set the PYTHONPYCACHEPREFIX environment variable
project_path = os.path.dirname(os.path.abspath(__file__))
cache_path = os.path.join(project_path, '.cache')
os.environ['PYTHONPYCACHEPREFIX'] = cache_path

# Replace 'main.py' with the entry point script of your project
main_script = os.path.join(project_path, 'server.py')

# Run the main script with the modified environment
subprocess.run([sys.executable, main_script], env=os.environ)

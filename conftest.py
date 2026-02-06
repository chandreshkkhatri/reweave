import sys
from pathlib import Path

sys.pycache_prefix = str(Path(__file__).parent / ".pycache")

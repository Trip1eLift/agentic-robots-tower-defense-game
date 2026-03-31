# Adds repo root to sys.path so "from backend.X import ..." works in tests
# without requiring pip install -e or pyproject.toml pythonpath config.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

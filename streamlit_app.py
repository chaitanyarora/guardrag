import sys
from pathlib import Path

# Add repository root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Execute the main Streamlit application
from app.streamlit_app import *

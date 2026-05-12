import sys
import os

# Set test environment variables BEFORE importing anything from app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "1"

import sys
from unittest.mock import MagicMock

# Mock heavy ML libraries to prevent hanging on import
sys.modules['google.generativeai'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['faiss'] = MagicMock()
sys.modules['whisper'] = MagicMock()

# Mock platform to avoid WMI hang
mock_platform = MagicMock()
mock_platform.system.return_value = "Windows"
sys.modules['platform'] = mock_platform

# Add the backend directory to sys.path so that 'app' package can be imported in tests
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

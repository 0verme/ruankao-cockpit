"""Enable the documented ``python -m unittest tests.test_*`` invocation."""
from pathlib import Path
import sys

_TESTS_DIR = str(Path(__file__).resolve().parent)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

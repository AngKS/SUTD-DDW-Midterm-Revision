"""Shared pytest configuration for the project.

Lives at the repo root so every test (root-level ``test_library.py`` and the
suites under ``tests/``) can import the application modules — ``library``,
``Models.Algorithms``, ``Utilities.GraphView`` — regardless of pytest's import
mode or the directory pytest was invoked from.
"""
import logging
import sys
from pathlib import Path

# Make the project root importable (``import library``, ``from Models...``).
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Streamlit's AppTest emits a WARNING-level log line for every rendered frame
# ("missing ScriptRunContext", "use_container_width deprecated"). Sorting a
# small array produces dozens of frames, which would bury the pytest output.
# Silence everything below ERROR so the test report stays readable.
logging.getLogger("streamlit").setLevel(logging.ERROR)

"""Test configuration for pytest."""
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_collection_modifyitems(session, config, items):
    skip_paths = ['ontochat/ontolib.py', 'ontochat\\ontolib.py']
    for item in items.copy():
        try:
            path = str(item.path) if hasattr(item, 'path') else str(item.fspath)
            if any(skip in path for skip in skip_paths):
                items.remove(item)
        except (AttributeError, TypeError):
            continue

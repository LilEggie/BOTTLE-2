"""
Project definitions.
"""

__all__ = ["ROOT_DIR", "RESOURCE_DIR", "LOG_DIR"]
__version__ = "1.0.0"
__author__ = "Eggie"


from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent
"""
The project root directory.
"""

RESOURCE_DIR = ROOT_DIR / "resources"
"""
The resource directory.

When this module is imported for the first time, this directory will be created
if it doesn't exist.
"""
RESOURCE_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = ROOT_DIR / "logs"
"""
The log directory.

When this module is imported for the first time, this directory will be created
if it doesn't exist.
"""
LOG_DIR.mkdir(parents=True, exist_ok=True)

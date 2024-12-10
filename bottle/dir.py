"""
Project directories.
"""

__all__ = ["root", "resources", "logs"]
__version__ = "1.0.0"
__author__ = "Eggie"


from pathlib import Path


root = Path(__file__).parent.parent
"""The project root directory"""
root.mkdir(parents=True, exist_ok=True)


resources = root / "resources"
"""The resources directory"""
resources.mkdir(parents=True, exist_ok=True)


logs = root / "logs"
"""The logs directory"""
logs.mkdir(parents=True, exist_ok=True)

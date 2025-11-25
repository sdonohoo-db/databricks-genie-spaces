"""
Databricks Genie Spaces Management

An extension of databricks-ai-bridge for managing Genie Space lifecycle (CRUD operations).
This package provides administrative functions for creating, updating, and managing Genie Spaces,
complementing the query/interaction capabilities in databricks-ai-bridge.

Based on: https://docs.databricks.com/api/workspace/genie
"""

__version__ = "0.1.0"
__author__ = "Databricks"

from .spaces import (
    GenieSpacesManager,
    GenieSpaceError,
    create_spaces_manager,
)

__all__ = [
    "GenieSpacesManager",
    "GenieSpaceError",
    "create_spaces_manager",
    "__version__",
]

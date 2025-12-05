"""
Databricks Genie Spaces Management

Extension package providing Beta Genie Space APIs not yet available in the Databricks SDK.

Beta APIs (this package):
    - create_space() - Create a new Genie Space
    - update_space() - Update an existing Genie Space  
    - get_space(include_serialized_space=True) - Export space configuration

Public Preview APIs (use Databricks SDK directly):
    - w.genie.list_spaces() - List all Genie Spaces
    - w.genie.get_space(space_id) - Get basic space details
    - w.genie.trash_space(space_id) - Delete a Genie Space

SDK Reference: https://databricks-sdk-py.readthedocs.io/en/stable/workspace/dashboards/genie.html
API Reference: https://docs.databricks.com/api/workspace/genie
"""

__version__ = "0.1.0"
__author__ = "Databricks"

from .spaces import (
    GenieSpacesManager,
    GenieSpaceError,
    create_spaces_manager,
)

# Re-export GenieSpace from SDK for convenience
from databricks.sdk.service.dashboards import GenieSpace

__all__ = [
    "GenieSpacesManager",
    "GenieSpaceError",
    "GenieSpace",
    "create_spaces_manager",
    "__version__",
]

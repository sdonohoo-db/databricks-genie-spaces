"""
Databricks Genie Spaces Management

Extension package providing Beta Genie Space APIs not yet available in the Databricks SDK.
API Reference: https://docs.databricks.com/api/workspace/genie

This module provides Beta APIs for managing Genie Spaces:
- get_space: Get space details with include_serialized_space option (for export)
- create_space: Create a new Genie Space (Beta)
- update_space: Update an existing Genie Space (Beta)

For Public Preview APIs, use the Databricks SDK directly:
- w.genie.list_spaces() - List all Genie Spaces
- w.genie.get_space(space_id) - Get basic space details
- w.genie.trash_space(space_id) - Delete a Genie Space

See: https://databricks-sdk-py.readthedocs.io/en/stable/workspace/dashboards/genie.html
"""

import logging
from typing import Dict, Optional, Any
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieSpace

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logging.info("mlflow not available, tracing will be disabled")


class GenieSpaceError(Exception):
    """Exception raised for Genie Space management errors"""
    
    def __init__(self, status_code: int, message: str, response: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.response = response
        super().__init__(f"Genie Space Error ({status_code}): {message}")


class GenieSpacesManager:
    """
    Manager for Databricks Genie Space Beta APIs
    
    This class provides Beta APIs for Genie Space management that are not yet
    available in the Databricks SDK. For Public Preview APIs, use the SDK directly.
    
    Beta APIs (this package):
        - get_space(space_id, include_serialized_space=True) - Export configuration
        - create_space() - Create a new Genie Space
        - update_space() - Update an existing Genie Space
    
    Public Preview APIs (use Databricks SDK):
        - w.genie.list_spaces() - List all spaces
        - w.genie.get_space(space_id) - Get basic space details
        - w.genie.trash_space(space_id) - Delete a space
    
    Example:
        >>> from databricks.sdk import WorkspaceClient
        >>> from databricks_genie_spaces import GenieSpacesManager
        >>> 
        >>> w = WorkspaceClient()
        >>> manager = GenieSpacesManager(w)
        >>> 
        >>> # Use SDK for listing (Public Preview)
        >>> spaces = w.genie.list_spaces()
        >>> 
        >>> # Use this package for create/update (Beta)
        >>> template = manager.get_space("template_id", include_serialized_space=True)
        >>> new_space = manager.create_space(
        ...     warehouse_id="...",
        ...     parent_path="/Workspace/...",
        ...     serialized_space=template.serialized_space
        ... )
        >>> print(f"Created: {new_space.space_id}")
    
    API Reference: https://docs.databricks.com/api/workspace/genie
    """
    
    def __init__(self, workspace_client: WorkspaceClient):
        """
        Initialize the Genie Spaces Manager
        
        Args:
            workspace_client: Databricks WorkspaceClient instance
                            (from databricks.sdk import WorkspaceClient)
        """
        self.client = workspace_client
        self._api_client = workspace_client.api_client
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Genie API
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (relative to /api/2.0/genie/)
            params: Query parameters
            data: Request body data
            
        Returns:
            Response JSON as dictionary
            
        Raises:
            GenieSpaceError: If the request fails
        """
        path = f"/api/2.0/genie/{endpoint.lstrip('/')}"
        
        try:
            # Use the ApiClient's do method for consistency with databricks-sdk patterns
            response = self._api_client.do(
                method=method,
                path=path,
                query=params,
                body=data,
                headers={"Content-Type": "application/json"}
            )
            
            return response or {}
            
        except Exception as e:
            error_msg = str(e)
            status_code = getattr(e, 'status_code', 0) if hasattr(e, 'status_code') else 0
            
            # Handle 501 error specifically (not enabled for preview)
            if status_code == 501:
                raise GenieSpaceError(
                    501,
                    "This API is not yet supported. Your workspace may not be enabled for the Genie API private preview.",
                    None
                )
            
            raise GenieSpaceError(status_code, error_msg, None)
    
    def create_space(
        self,
        warehouse_id: str,
        parent_path: str,
        serialized_space: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> GenieSpace:
        """
        Create a new Genie Space (Beta API)
        
        API: POST /api/2.0/genie/spaces
        Docs: https://docs.databricks.com/api/workspace/genie/createspace
        
        Args:
            warehouse_id: ID of the SQL warehouse to use for this space
            parent_path: Workspace folder path where the space will be created
                        (e.g., "/Workspace/Users/user@company.com/Genie Spaces")
            serialized_space: JSON string of space configuration (required).
                            Export from an existing space using get_space() with
                            include_serialized_space=True, or create a minimal config.
            title: Optional space title (can override title in serialized_space)
            description: Optional space description (can override description in serialized_space)
            
        Returns:
            GenieSpace: The created space object (consistent with SDK patterns)
            
        Example:
            >>> # Create from exported configuration
            >>> manager = GenieSpacesManager(workspace_client)
            >>> # First, export an existing space
            >>> exported = manager.get_space("existing_space_id", include_serialized_space=True)
            >>> serialized_config = exported.serialized_space
            >>> 
            >>> # Create new space from configuration
            >>> space = manager.create_space(
            ...     warehouse_id="abc123def456",
            ...     parent_path="/Workspace/Users/user@example.com/Genie Spaces",
            ...     serialized_space=serialized_config,
            ...     title="My New Space",
            ...     description="A space for analytics"
            ... )
            >>> print(f"Created space: {space.space_id}")
        """
        data = {
            "warehouse_id": warehouse_id,
            "parent_path": parent_path,
            "serialized_space": serialized_space
        }
        
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        
        if MLFLOW_AVAILABLE:
            with mlflow.start_span(name="create_space") as span:
                span.set_attribute("warehouse_id", warehouse_id)
                span.set_attribute("title", title or "")
                result = self._make_request("POST", "spaces", data=data)
                span.set_attribute("space_id", result.get("space_id", ""))
                return GenieSpace.from_dict(result)
        else:
            result = self._make_request("POST", "spaces", data=data)
            return GenieSpace.from_dict(result)
    
    def get_space(
        self,
        space_id: str,
        include_serialized_space: bool = False
    ) -> GenieSpace:
        """
        Get details of a specific Genie Space (with serialized_space export option)
        
        API: GET /api/2.0/genie/spaces/{space_id}
        Docs: https://docs.databricks.com/api/workspace/genie/getspace
        
        Note: The SDK's w.genie.get_space() does not support include_serialized_space.
        Use this method when you need to export space configurations.
        
        Args:
            space_id: The unique identifier of the Genie Space
            include_serialized_space: If True, includes the full serialized space configuration
                                     (required for export/import operations)
            
        Returns:
            GenieSpace: Space object with attributes:
                - space_id: The space identifier
                - title: Space title
                - description: Space description
                - warehouse_id: Associated SQL warehouse ID
                - serialized_space: JSON string of full space config (if requested)
                
        Example:
            >>> # Get basic space info
            >>> space = manager.get_space("01ef274d35a310b5bffd01dadcbaf577")
            >>> print(space.title)
            
            >>> # Export space configuration
            >>> exported = manager.get_space("01ef274d35a310b5bffd01dadcbaf577", 
            ...                              include_serialized_space=True)
            >>> config = exported.serialized_space
        """
        params = {}
        if include_serialized_space:
            params["include_serialized_space"] = "true"
        
        if MLFLOW_AVAILABLE:
            with mlflow.start_span(name="get_space") as span:
                span.set_attribute("space_id", space_id)
                span.set_attribute("include_serialized_space", include_serialized_space)
                result = self._make_request("GET", f"spaces/{space_id}", params=params)
                return GenieSpace.from_dict(result)
        else:
            result = self._make_request("GET", f"spaces/{space_id}", params=params)
            return GenieSpace.from_dict(result)
    
    def update_space(
        self,
        space_id: str,
        warehouse_id: Optional[str] = None,
        parent_path: Optional[str] = None,
        serialized_space: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> GenieSpace:
        """
        Update an existing Genie Space (Beta API)
        
        API: PATCH /api/2.0/genie/spaces/{space_id}
        Docs: https://docs.databricks.com/api/workspace/genie/updatespace
        
        All parameters (except space_id) are optional - only provided fields will be updated.
        
        Args:
            space_id: The unique identifier of the Genie Space to update
            warehouse_id: New SQL warehouse ID
            parent_path: New workspace folder path
            serialized_space: New space configuration (JSON string)
            title: New space title
            description: New space description
            
        Returns:
            GenieSpace: The updated space object
            
        Example:
            >>> # Update just the title
            >>> updated = manager.update_space("01ef274d35a310b5bffd01dadcbaf577", 
            ...                                title="Updated Title")
            >>> print(updated.title)
            
            >>> # Update configuration from export
            >>> manager.update_space("01ef274d35a310b5bffd01dadcbaf577",
            ...                      serialized_space=exported_config)
        """
        data = {}
        
        if warehouse_id:
            data["warehouse_id"] = warehouse_id
        if parent_path:
            data["parent_path"] = parent_path
        if serialized_space:
            data["serialized_space"] = serialized_space
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        
        if not data:
            raise ValueError("At least one field must be provided to update")
        
        if MLFLOW_AVAILABLE:
            with mlflow.start_span(name="update_space") as span:
                span.set_attribute("space_id", space_id)
                span.set_attribute("fields_updated", list(data.keys()))
                result = self._make_request("PATCH", f"spaces/{space_id}", data=data)
                return GenieSpace.from_dict(result)
        else:
            result = self._make_request("PATCH", f"spaces/{space_id}", data=data)
            return GenieSpace.from_dict(result)


def create_spaces_manager(workspace_client: Optional[WorkspaceClient] = None) -> GenieSpacesManager:
    """
    Create a Genie Spaces Manager
    
    Args:
        workspace_client: Optional WorkspaceClient instance. If not provided,
                         a new WorkspaceClient will be created using default
                         authentication (environment variables or .databrickscfg)
        
    Returns:
        Configured GenieSpacesManager instance
        
    Example:
        >>> # With explicit client
        >>> from databricks.sdk import WorkspaceClient
        >>> w = WorkspaceClient(host="...", token="...")
        >>> manager = create_spaces_manager(w)
        
        >>> # With default authentication
        >>> manager = create_spaces_manager()
    """
    if workspace_client is None:
        workspace_client = WorkspaceClient()
    
    return GenieSpacesManager(workspace_client)


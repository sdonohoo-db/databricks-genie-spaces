"""
Databricks Genie Spaces Management

Extension of databricks-ai-bridge for Genie Space CRUD operations.
API Reference: https://docs.databricks.com/api/workspace/genie

This module provides administrative functions for managing Genie Spaces:
- list_spaces: List all Genie Spaces
- create_space: Create a new Genie Space
- get_space: Get details of a specific Genie Space
- update_space: Update an existing Genie Space
- trash_space: Delete/trash a Genie Space

These operations complement the query/interaction capabilities provided by
the GenieClient in databricks-ai-bridge.
"""

import logging
from typing import Dict, List, Optional, Any
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import ApiClient

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
    Manager for Databricks Genie Space administrative operations
    
    This class extends the functionality of databricks-ai-bridge by providing
    CRUD operations for Genie Spaces. Use this for space management tasks,
    and use databricks_ai_bridge.genie.GenieClient for querying spaces.
    
    Example:
        >>> from databricks.sdk import WorkspaceClient
        >>> from databricks_genie_spaces import GenieSpacesManager
        >>> 
        >>> w = WorkspaceClient()
        >>> manager = GenieSpacesManager(w)
        >>> spaces = manager.list_spaces()
        >>> 
        >>> # For querying, use databricks-ai-bridge:
        >>> from databricks_ai_bridge.genie import GenieClient
        >>> genie = GenieClient(w, space_id="...")
        >>> response = genie.ask_question("Show me sales by region")
    
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
    
    def list_spaces(
        self,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all Genie Spaces in the workspace
        
        API: GET /api/2.0/genie/spaces
        Docs: https://docs.databricks.com/api/workspace/genie/listspaces
        
        Args:
            page_size: Maximum number of spaces to return per page
            page_token: Token for pagination (from previous response)
            
        Returns:
            Dictionary containing:
                - spaces: List of space objects
                - next_page_token: Token for next page (if more results exist)
                
        Example:
            >>> manager = GenieSpacesManager(workspace_client)
            >>> result = manager.list_spaces()
            >>> for space in result.get('spaces', []):
            ...     print(f"{space['space_id']}: {space['title']}")
        """
        params = {}
        if page_size:
            params["page_size"] = page_size
        if page_token:
            params["page_token"] = page_token
        
        if MLFLOW_AVAILABLE:
            with mlflow.start_span(name="list_spaces") as span:
                span.set_attribute("page_size", page_size)
                result = self._make_request("GET", "spaces", params=params)
                span.set_attribute("num_spaces", len(result.get("spaces", [])))
                return result
        else:
            return self._make_request("GET", "spaces", params=params)
    
    def create_space(
        self,
        warehouse_id: str,
        parent_path: str,
        serialized_space: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Genie Space
        
        API: POST /api/2.0/genie/spaces
        Docs: https://docs.databricks.com/api/workspace/genie/createspace
        
        Args:
            warehouse_id: ID of the SQL warehouse to use for this space
            parent_path: Workspace folder path where the space will be created
                        (e.g., "/Workspace/Users/user@company.com/Genie Spaces")
            serialized_space: Optional JSON string of exported space configuration
            title: Optional space title
            description: Optional space description
            
        Returns:
            Dictionary containing the created space details including space_id
            
        Example:
            >>> manager = GenieSpacesManager(workspace_client)
            >>> space = manager.create_space(
            ...     warehouse_id="abc123def456",
            ...     parent_path="/Workspace/Users/user@example.com/Genie Spaces",
            ...     title="My New Space",
            ...     description="A space for analytics"
            ... )
            >>> print(f"Created space: {space['space_id']}")
        """
        data = {
            "warehouse_id": warehouse_id,
            "parent_path": parent_path
        }
        
        if serialized_space:
            data["serialized_space"] = serialized_space
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
                return result
        else:
            return self._make_request("POST", "spaces", data=data)
    
    def get_space(
        self,
        space_id: str,
        include_serialized_space: bool = False
    ) -> Dict[str, Any]:
        """
        Get details of a specific Genie Space
        
        API: GET /api/2.0/genie/spaces/{space_id}
        Docs: https://docs.databricks.com/api/workspace/genie/getspace
        
        Args:
            space_id: The unique identifier of the Genie Space
            include_serialized_space: If True, includes the full serialized space configuration
                                     (required for export/import operations)
            
        Returns:
            Dictionary containing:
                - space_id: The space identifier
                - title: Space title
                - description: Space description
                - warehouse_id: Associated SQL warehouse ID
                - serialized_space: JSON string of full space config (if requested)
                
        Example:
            >>> # Get basic space info
            >>> space = manager.get_space("01ef274d35a310b5bffd01dadcbaf577")
            >>> print(space['title'])
            
            >>> # Export space configuration
            >>> exported = manager.get_space("01ef274d35a310b5bffd01dadcbaf577", 
            ...                              include_serialized_space=True)
            >>> config = exported['serialized_space']
        """
        params = {}
        if include_serialized_space:
            params["include_serialized_space"] = "true"
        
        if MLFLOW_AVAILABLE:
            with mlflow.start_span(name="get_space") as span:
                span.set_attribute("space_id", space_id)
                span.set_attribute("include_serialized_space", include_serialized_space)
                result = self._make_request("GET", f"spaces/{space_id}", params=params)
                return result
        else:
            return self._make_request("GET", f"spaces/{space_id}", params=params)
    
    def update_space(
        self,
        space_id: str,
        warehouse_id: Optional[str] = None,
        parent_path: Optional[str] = None,
        serialized_space: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing Genie Space
        
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
            Dictionary containing the updated space details
            
        Example:
            >>> # Update just the title
            >>> manager.update_space("01ef274d35a310b5bffd01dadcbaf577", 
            ...                      title="Updated Title")
            
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
                return result
        else:
            return self._make_request("PATCH", f"spaces/{space_id}", data=data)
    
    def trash_space(self, space_id: str) -> Dict[str, Any]:
        """
        Delete (trash) a Genie Space
        
        API: DELETE /api/2.0/genie/spaces/{space_id}
        Docs: https://docs.databricks.com/api/workspace/genie/trashspace
        
        Note: This moves the space to trash. It may be recoverable depending on
        workspace settings.
        
        Args:
            space_id: The unique identifier of the Genie Space to delete
            
        Returns:
            Empty dictionary on success
            
        Example:
            >>> manager.trash_space("01ef274d35a310b5bffd01dadcbaf577")
        """
        if MLFLOW_AVAILABLE:
            with mlflow.start_span(name="trash_space") as span:
                span.set_attribute("space_id", space_id)
                result = self._make_request("DELETE", f"spaces/{space_id}")
                return result
        else:
            return self._make_request("DELETE", f"spaces/{space_id}")


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


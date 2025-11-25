"""
Tests for Databricks Genie Spaces Management
"""

import json
from unittest.mock import Mock, patch, MagicMock
import pytest

from databricks_genie_spaces import (
    GenieSpacesManager,
    GenieSpaceError,
    create_spaces_manager,
)


@pytest.fixture
def mock_workspace_client():
    """Create a mock WorkspaceClient"""
    mock_client = Mock()
    mock_api_client = Mock()
    mock_client.api_client = mock_api_client
    return mock_client


def test_manager_creation(mock_workspace_client):
    """Test GenieSpacesManager creation"""
    manager = GenieSpacesManager(mock_workspace_client)
    assert isinstance(manager, GenieSpacesManager)
    assert manager.client == mock_workspace_client


def test_create_spaces_manager():
    """Test create_spaces_manager helper"""
    with patch('databricks_genie_spaces.spaces.WorkspaceClient') as mock_ws:
        mock_ws.return_value = Mock()
        manager = create_spaces_manager()
        assert isinstance(manager, GenieSpacesManager)


def test_list_spaces(mock_workspace_client):
    """Test list_spaces method"""
    mock_response = {
        "spaces": [
            {"space_id": "123", "title": "Test Space 1"},
            {"space_id": "456", "title": "Test Space 2"}
        ]
    }
    mock_workspace_client.api_client.do.return_value = mock_response
    
    manager = GenieSpacesManager(mock_workspace_client)
    result = manager.list_spaces()
    
    assert "spaces" in result
    assert len(result["spaces"]) == 2
    assert result["spaces"][0]["space_id"] == "123"
    
    mock_workspace_client.api_client.do.assert_called_once()
    call_args = mock_workspace_client.api_client.do.call_args
    assert call_args[1]["method"] == "GET"
    assert "spaces" in call_args[1]["path"]


def test_get_space(mock_workspace_client):
    """Test get_space method"""
    mock_response = {
        "space_id": "123",
        "title": "Test Space"
    }
    mock_workspace_client.api_client.do.return_value = mock_response
    
    manager = GenieSpacesManager(mock_workspace_client)
    result = manager.get_space("123")
    
    assert result["space_id"] == "123"
    assert result["title"] == "Test Space"
    
    call_args = mock_workspace_client.api_client.do.call_args
    assert "spaces/123" in call_args[1]["path"]


def test_get_space_with_serialized(mock_workspace_client):
    """Test get_space with serialized_space"""
    mock_response = {
        "space_id": "123",
        "title": "Test Space",
        "serialized_space": "{\"version\": 1}"
    }
    mock_workspace_client.api_client.do.return_value = mock_response
    
    manager = GenieSpacesManager(mock_workspace_client)
    result = manager.get_space("123", include_serialized_space=True)
    
    assert "serialized_space" in result
    
    call_args = mock_workspace_client.api_client.do.call_args
    assert call_args[1]["query"]["include_serialized_space"] == "true"


def test_create_space(mock_workspace_client):
    """Test create_space method"""
    mock_response = {
        "space_id": "789",
        "title": "New Space"
    }
    mock_workspace_client.api_client.do.return_value = mock_response
    
    manager = GenieSpacesManager(mock_workspace_client)
    result = manager.create_space(
        warehouse_id="abc123",
        parent_path="/Workspace/Users/test",
        title="New Space"
    )
    
    assert result["space_id"] == "789"
    assert result["title"] == "New Space"
    
    call_args = mock_workspace_client.api_client.do.call_args
    assert call_args[1]["method"] == "POST"
    assert call_args[1]["body"]["warehouse_id"] == "abc123"
    assert call_args[1]["body"]["title"] == "New Space"


def test_update_space(mock_workspace_client):
    """Test update_space method"""
    mock_response = {
        "space_id": "123",
        "title": "Updated Title"
    }
    mock_workspace_client.api_client.do.return_value = mock_response
    
    manager = GenieSpacesManager(mock_workspace_client)
    result = manager.update_space(space_id="123", title="Updated Title")
    
    assert result["title"] == "Updated Title"
    
    call_args = mock_workspace_client.api_client.do.call_args
    assert call_args[1]["method"] == "PATCH"
    assert "spaces/123" in call_args[1]["path"]
    assert call_args[1]["body"]["title"] == "Updated Title"


def test_update_space_no_fields_error(mock_workspace_client):
    """Test update_space raises error with no fields"""
    manager = GenieSpacesManager(mock_workspace_client)
    
    with pytest.raises(ValueError, match="At least one field must be provided"):
        manager.update_space("123")


def test_trash_space(mock_workspace_client):
    """Test trash_space method"""
    mock_workspace_client.api_client.do.return_value = {}
    
    manager = GenieSpacesManager(mock_workspace_client)
    result = manager.trash_space("123")
    
    assert result == {}
    
    call_args = mock_workspace_client.api_client.do.call_args
    assert call_args[1]["method"] == "DELETE"
    assert "spaces/123" in call_args[1]["path"]


def test_genie_space_error():
    """Test GenieSpaceError exception"""
    error = GenieSpaceError(404, "Not found", {"error": "details"})
    
    assert error.status_code == 404
    assert error.message == "Not found"
    assert error.response == {"error": "details"}
    assert "404" in str(error)


def test_api_error_handling(mock_workspace_client):
    """Test error handling in API calls"""
    # Simulate an API error
    mock_error = Exception("API Error")
    mock_error.status_code = 404
    mock_workspace_client.api_client.do.side_effect = mock_error
    
    manager = GenieSpacesManager(mock_workspace_client)
    
    with pytest.raises(GenieSpaceError) as exc_info:
        manager.get_space("invalid_id")
    
    assert exc_info.value.status_code == 404


def test_501_error_handling(mock_workspace_client):
    """Test 501 error specific handling"""
    mock_error = Exception("Not supported")
    mock_error.status_code = 501
    mock_workspace_client.api_client.do.side_effect = mock_error
    
    manager = GenieSpacesManager(mock_workspace_client)
    
    with pytest.raises(GenieSpaceError) as exc_info:
        manager.list_spaces()
    
    assert exc_info.value.status_code == 501
    assert "not yet supported" in exc_info.value.message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


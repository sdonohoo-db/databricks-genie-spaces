# Databricks Genie Spaces Management

**An extension of [databricks-ai-bridge](https://github.com/databricks/databricks-ai-bridge) for Genie Space administrative operations.**

This package provides CRUD (Create, Read, Update, Delete) operations for managing Databricks Genie Spaces, complementing the query/interaction capabilities in `databricks-ai-bridge`.

## Relationship to databricks-ai-bridge

| Package | Purpose | Use Cases |
|---------|---------|-----------|
| **databricks-ai-bridge** | Query & interact with Genie Spaces | Ask questions, get answers, conversation management |
| **databricks-genie-spaces** (this package) | Manage Genie Space lifecycle | Create, update, export, import, delete spaces |

**Use together:**
- Use `databricks_ai_bridge.genie.GenieClient` to **query** existing spaces
- Use `databricks_genie_spaces.GenieSpacesManager` to **manage** spaces

## Features

- ✅ **List Spaces**: Enumerate all Genie Spaces in workspace
- ✅ **Create Spaces**: Create new Genie Spaces with configuration
- ✅ **Get/Export Spaces**: Retrieve space details and full configuration
- ✅ **Update Spaces**: Modify existing space configuration
- ✅ **Delete/Trash Spaces**: Remove spaces (recoverable via trash)
- ✅ **MLflow Tracing**: Optional MLflow integration for observability
- ✅ **SDK Integration**: Uses `databricks.sdk.WorkspaceClient` for consistency

## Installation

```bash
pip install databricks-genie-spaces
```

This will automatically install:
- `databricks-sdk` - For workspace authentication and API access
- `databricks-ai-bridge` - For core Genie functionality

**Optional:** Install with MLflow tracing support:
```bash
pip install databricks-genie-spaces[mlflow]
```

Or install from source:
```bash
pip install git+https://github.com/databricks/databricks-genie-spaces.git
```

## Quick Start

### Managing Spaces (this package)

```python
from databricks.sdk import WorkspaceClient
from databricks_genie_spaces import GenieSpacesManager

# Initialize
w = WorkspaceClient()  # Uses environment variables or .databrickscfg
manager = GenieSpacesManager(w)

# List all spaces
spaces = manager.list_spaces()
for space in spaces.get('spaces', []):
    print(f"{space['space_id']}: {space['title']}")

# Export an existing space configuration to use as template
template = manager.get_space("template_space_id", include_serialized_space=True)
serialized_config = template['serialized_space']

# Create a new space from the configuration
new_space = manager.create_space(
    warehouse_id="your_warehouse_id",
    parent_path="/Workspace/Users/user@example.com/Genie Spaces",
    serialized_space=serialized_config,
    title="Sales Analytics",
    description="Space for sales data analysis"
)
print(f"Created: {new_space['space_id']}")

# Export a space (with full configuration)
exported = manager.get_space(
    space_id="your_space_id",
    include_serialized_space=True
)
config = exported['serialized_space']

# Update a space
manager.update_space(
    space_id="your_space_id",
    title="Sales Analytics (Updated)"
)

# Delete a space
manager.trash_space("your_space_id")
```

### Querying Spaces (databricks-ai-bridge)

```python
from databricks.sdk import WorkspaceClient
from databricks_ai_bridge.genie import GenieClient

# Initialize for querying
w = WorkspaceClient()
genie = GenieClient(w, space_id="your_space_id")

# Ask questions
response = genie.ask_question("What were total sales last quarter?")
print(response.result)

# Continue conversation
response2 = genie.ask_question(
    "Break that down by region",
    conversation_id=response.conversation_id
)
print(response2.result)
```

## Complete Workflow Example

```python
from databricks.sdk import WorkspaceClient
from databricks_genie_spaces import GenieSpacesManager
from databricks_ai_bridge.genie import GenieClient

# Setup
w = WorkspaceClient()
manager = GenieSpacesManager(w)

# 1. Create a space from a template
template = manager.get_space("template_space_id", include_serialized_space=True)
new_space = manager.create_space(
    warehouse_id="abc123",
    parent_path="/Workspace/Users/user@example.com/Genie Spaces",
    serialized_space=template['serialized_space'],
    title="Customer Analytics"
)
space_id = new_space['space_id']

# 2. Query the space
genie = GenieClient(w, space_id=space_id)
response = genie.ask_question("Show me top 10 customers by revenue")
print(response.result)

# 3. Export configuration for backup
exported = manager.get_space(space_id, include_serialized_space=True)
import json
with open("backup.json", 'w') as f:
    json.dump(exported, f)

# 4. Update space configuration
manager.update_space(
    space_id,
    description="Updated analytics space"
)
```

## API Methods

All methods correspond to the [Databricks Genie API](https://docs.databricks.com/api/workspace/genie):

### `list_spaces(page_size=None, page_token=None)`

List all Genie Spaces in the workspace.

**Docs:** [listspaces](https://docs.databricks.com/api/workspace/genie/listspaces)

### `create_space(warehouse_id, parent_path, serialized_space, title=None, description=None)`

Create a new Genie Space. The `serialized_space` parameter is required and contains the space configuration (export from an existing space using `get_space()` with `include_serialized_space=True`).

**Docs:** [createspace](https://docs.databricks.com/api/workspace/genie/createspace)

### `get_space(space_id, include_serialized_space=False)`

Get details of a specific Genie Space. Set `include_serialized_space=True` to export full configuration.

**Docs:** [getspace](https://docs.databricks.com/api/workspace/genie/getspace)

### `update_space(space_id, **fields)`

Update an existing Genie Space. All fields except `space_id` are optional.

**Docs:** [updatespace](https://docs.databricks.com/api/workspace/genie/updatespace)

### `trash_space(space_id)`

Delete (trash) a Genie Space. May be recoverable depending on workspace settings.

**Docs:** [trashspace](https://docs.databricks.com/api/workspace/genie/trashspace)

## Authentication

This package uses `databricks.sdk.WorkspaceClient` for authentication, which supports:

1. **Environment Variables:**
   ```bash
   export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
   export DATABRICKS_TOKEN="dapi..."
   ```

2. **Configuration File** (`~/.databrickscfg`):
   ```ini
   [DEFAULT]
   host = https://your-workspace.cloud.databricks.com
   token = dapi...
   ```

3. **Explicit Credentials:**
   ```python
   from databricks.sdk import WorkspaceClient
   w = WorkspaceClient(host="...", token="...")
   manager = GenieSpacesManager(w)
   ```

See [Databricks SDK Authentication](https://databricks-sdk-py.readthedocs.io/en/latest/authentication.html) for more details.

## Error Handling

```python
from databricks_genie_spaces import GenieSpacesManager, GenieSpaceError

manager = GenieSpacesManager(workspace_client)

try:
    space = manager.get_space("invalid_id")
except GenieSpaceError as e:
    if e.status_code == 404:
        print("Space not found")
    elif e.status_code == 501:
        print("Workspace not enabled for Genie API")
    elif e.status_code == 403:
        print("Permission denied")
    else:
        print(f"Error {e.status_code}: {e.message}")
```

### Common Error Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 400 | Bad Request | Invalid parameters (check warehouse_id, parent_path) |
| 401 | Unauthorized | Invalid or expired authentication token |
| 403 | Forbidden | Insufficient permissions on space or parent path |
| 404 | Not Found | Space doesn't exist or was deleted |
| 501 | Not Implemented | Workspace not enabled for Genie API private preview |

## MLflow Tracing

When MLflow is available, operations are automatically traced for observability:

```python
import mlflow
from databricks_genie_spaces import GenieSpacesManager

# Tracing is automatic if mlflow is installed
mlflow.set_experiment("/my-experiments/genie-management")

with mlflow.start_run():
    manager = GenieSpacesManager(workspace_client)
    
    # These operations will be traced
    spaces = manager.list_spaces()  # Creates "list_spaces" span
    space = manager.create_space(...)  # Creates "create_space" span
```

## Use Cases

### Export/Import Across Workspaces

```python
# Export from source workspace
source_w = WorkspaceClient(host=source_host, token=source_token)
source_mgr = GenieSpacesManager(source_w)
exported = source_mgr.get_space(space_id, include_serialized_space=True)

# Import to target workspace
target_w = WorkspaceClient(host=target_host, token=target_token)
target_mgr = GenieSpacesManager(target_w)
new_space = target_mgr.create_space(
    warehouse_id=target_warehouse,
    parent_path=target_path,
    serialized_space=exported['serialized_space'],
    title=exported['title'] + " (Copy)"
)
```

### Backup All Spaces

```python
import json
from datetime import datetime

manager = GenieSpacesManager(workspace_client)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

spaces = manager.list_spaces()
for space in spaces.get('spaces', []):
    space_id = space['space_id']
    exported = manager.get_space(space_id, include_serialized_space=True)
    
    filename = f"backup_{space_id}_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(exported, f, indent=2)
    
    print(f"Backed up: {space['title']}")
```

### Bulk Operations

```python
# Clone a space multiple times
template = manager.get_space(template_space_id, include_serialized_space=True)

for dept in ["Sales", "Marketing", "Engineering"]:
    new_space = manager.create_space(
        warehouse_id=warehouse_id,
        parent_path=f"/Workspace/Departments/{dept}/Genie Spaces",
        serialized_space=template['serialized_space'],
        title=f"{dept} Analytics",
        description=f"Analytics space for {dept} department"
    )
    print(f"Created space for {dept}: {new_space['space_id']}")
```

## Requirements

- Python 3.8 or higher
- `databricks-sdk` >= 0.18.0
- `databricks-ai-bridge` >= 0.1.0
- Databricks workspace with Genie enabled
- Workspace must be enabled for Genie API (private preview)

## Permissions

- **List spaces**: Can View or higher on spaces
- **Get space**: Can View or higher on the specific space
- **Create space**: Can Edit on the parent folder
- **Update space**: Can Edit on the specific space
- **Trash space**: Can Edit on the specific space

## Links

- **API Documentation**: https://docs.databricks.com/api/workspace/genie
- **databricks-ai-bridge**: https://github.com/databricks/databricks-ai-bridge
- **Databricks SDK**: https://github.com/databricks/databricks-sdk-py
- **Genie Overview**: https://docs.databricks.com/en/genie/

## License

MIT

## Support

For Databricks support, contact your Solutions Architect or Databricks representative.

For issues with Genie API enablement (501 errors), contact your Databricks Solutions Architect.

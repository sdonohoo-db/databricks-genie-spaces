# Quick Start Guide

## Installation

```bash
pip install databricks-genie-spaces
```

This automatically installs:
- `databricks-sdk`
- `databricks-ai-bridge`

## Basic Usage

### Managing Spaces (CRUD Operations)

```python
from databricks.sdk import WorkspaceClient
from databricks_genie_spaces import GenieSpacesManager

# Initialize
w = WorkspaceClient()  # Uses default auth
manager = GenieSpacesManager(w)

# List spaces
spaces = manager.list_spaces()
print(spaces)

# Get a space
space = manager.get_space("space_id_here")
print(space['title'])

# Export a space (with configuration)
exported = manager.get_space("space_id_here", include_serialized_space=True)
config = exported['serialized_space']

# Create a space from a template or existing space
template = manager.get_space("template_space_id", include_serialized_space=True)
new_space = manager.create_space(
    warehouse_id="abc123",
    parent_path="/Workspace/Users/you@company.com/Genie Spaces",
    serialized_space=template['serialized_space'],
    title="My Space"
)

# Update a space
manager.update_space("space_id", title="New Title")

# Delete a space
manager.trash_space("space_id")
```

### Querying Spaces (Use databricks-ai-bridge)

```python
from databricks.sdk import WorkspaceClient
from databricks_ai_bridge.genie import GenieClient

w = WorkspaceClient()
genie = GenieClient(w, space_id="your_space_id")

# Ask questions
response = genie.ask_question("What were sales last quarter?")
print(response.result)
```

## Complete Workflow

```python
from databricks.sdk import WorkspaceClient
from databricks_genie_spaces import GenieSpacesManager
from databricks_ai_bridge.genie import GenieClient

w = WorkspaceClient()

# 1. Create a space (using genie-spaces)
manager = GenieSpacesManager(w)
# Get a template space configuration
template = manager.get_space("template_space_id", include_serialized_space=True)
new_space = manager.create_space(
    warehouse_id="abc123",
    parent_path="/Workspace/Users/user@example.com/Genie Spaces",
    serialized_space=template['serialized_space'],
    title="Sales Analytics"
)
space_id = new_space['space_id']

# 2. Query the space (using ai-bridge)
genie = GenieClient(w, space_id=space_id)
response = genie.ask_question("Show me top 10 customers")
print(response.result)

# 3. Export for backup (using genie-spaces)
exported = manager.get_space(space_id, include_serialized_space=True)
# Save exported...
```

## Authentication

Uses `databricks.sdk.WorkspaceClient` authentication:

**Environment Variables:**
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."
```

**Config File** (`~/.databrickscfg`):
```ini
[DEFAULT]
host = https://your-workspace.cloud.databricks.com
token = dapi...
```

## Package Relationship

| Package | Purpose |
|---------|---------|
| **databricks-ai-bridge** | Query & interact with spaces |
| **databricks-genie-spaces** | Manage space lifecycle (CRUD) |

Use both together for complete Genie functionality!

## API Reference

All methods map to [Databricks Genie API](https://docs.databricks.com/api/workspace/genie):

- `list_spaces()` → GET /genie/spaces
- `create_space()` → POST /genie/spaces
- `get_space()` → GET /genie/spaces/{id}
- `update_space()` → PATCH /genie/spaces/{id}
- `trash_space()` → DELETE /genie/spaces/{id}

## Next Steps

- Read [full README](README.md) for detailed documentation
- Check [examples](examples/) for more use cases
- See [databricks-ai-bridge](https://github.com/databricks/databricks-ai-bridge) for querying

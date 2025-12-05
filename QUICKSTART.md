# Quick Start Guide

## Installation

```bash
pip install databricks-genie-spaces
```

This automatically installs:
- `databricks-sdk`
- `databricks-ai-bridge`

## API Overview

> ⚠️ **Beta Notice**: The Create and Update Genie Space APIs are in Beta and may have breaking changes.

| API | Status | Where |
|-----|--------|-------|
| `list_spaces()`, `get_space()`, `trash_space()` | Public Preview | `databricks.sdk` (`w.genie.*`) |
| `create_space()`, `update_space()` | **Beta** | `databricks-genie-spaces` |
| `get_space(include_serialized_space=True)` | **Beta** | `databricks-genie-spaces` |

## Basic Usage

### Public Preview APIs (Databricks SDK)

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()  # Uses default auth

# List all spaces
spaces = w.genie.list_spaces()
for space in spaces.spaces:
    print(f"{space.space_id}: {space.title}")

# Get a space
space = w.genie.get_space("space_id_here")
print(space.title)

# Delete a space
w.genie.trash_space("space_id_here")
```

### Beta APIs (this package)

```python
from databricks.sdk import WorkspaceClient
from databricks_genie_spaces import GenieSpacesManager

w = WorkspaceClient()
manager = GenieSpacesManager(w)

# Export a space configuration (Beta - not in SDK)
exported = manager.get_space("space_id_here", include_serialized_space=True)
config = exported.serialized_space

# Create a space from configuration (Beta)
new_space = manager.create_space(
    warehouse_id="abc123",
    parent_path="/Workspace/Users/you@company.com/Genie Spaces",
    serialized_space=config,
    title="My New Space"
)
print(f"Created: {new_space.space_id}")

# Update a space (Beta)
updated = manager.update_space("space_id", title="New Title")
print(f"Updated: {updated.title}")
```

### Querying Spaces (databricks-ai-bridge)

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
manager = GenieSpacesManager(w)

# 1. Export template configuration (Beta API)
template = manager.get_space("template_space_id", include_serialized_space=True)

# 2. Create a new space (Beta API)
new_space = manager.create_space(
    warehouse_id="abc123",
    parent_path="/Workspace/Users/user@example.com/Genie Spaces",
    serialized_space=template.serialized_space,
    title="Sales Analytics"
)
space_id = new_space.space_id

# 3. Query the space (databricks-ai-bridge)
genie = GenieClient(w, space_id=space_id)
response = genie.ask_question("Show me top 10 customers")
print(response.result)

# 4. Delete when done (Public Preview - SDK)
w.genie.trash_space(space_id)
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
| **databricks.sdk** | Public Preview Genie APIs (list, get, trash) |
| **databricks-genie-spaces** | Beta APIs (create, update, export) |
| **databricks-ai-bridge** | Query & interact with spaces |

## API Reference

Beta APIs in this package:
- `create_space()` → POST /genie/spaces
- `update_space()` → PATCH /genie/spaces/{id}
- `get_space(include_serialized_space=True)` → GET /genie/spaces/{id}

Public Preview APIs in SDK:
- `w.genie.list_spaces()` → GET /genie/spaces
- `w.genie.get_space()` → GET /genie/spaces/{id}
- `w.genie.trash_space()` → DELETE /genie/spaces/{id}

See: https://databricks-sdk-py.readthedocs.io/en/stable/workspace/dashboards/genie.html

## Next Steps

- Read [full README](README.md) for detailed documentation
- Check [examples](examples/) for more use cases
- See [databricks-ai-bridge](https://github.com/databricks/databricks-ai-bridge) for querying

# Databricks notebook source
# MAGIC %md
# MAGIC # Databricks Genie Spaces Management - Basic Usage
# MAGIC
# MAGIC This notebook demonstrates the CRUD operations for managing Genie Spaces using the `databricks-genie-spaces` package.
# MAGIC
# MAGIC **Note:** For querying spaces (asking questions), use `databricks-ai-bridge` instead.
# MAGIC
# MAGIC ## Setup
# MAGIC
# MAGIC First, ensure the package is installed:
# MAGIC ```bash
# MAGIC %pip install databricks-genie-spaces
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install Package (if needed)

# COMMAND ----------

# Uncomment to install the package
# %pip install databricks-genie-spaces
# dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Libraries

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks_genie_spaces import GenieSpacesManager, GenieSpaceError
import json

# COMMAND ----------

# MAGIC %md
# MAGIC ## Initialize Workspace Client and Manager

# COMMAND ----------

# Initialize WorkspaceClient (uses default authentication)
w = WorkspaceClient()

# Create spaces manager
manager = GenieSpacesManager(w)

print("✅ Manager initialized successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Example 1: List All Genie Spaces
# MAGIC
# MAGIC List all Genie Spaces available in your workspace.

# COMMAND ----------

try:
    result = manager.list_spaces()
    spaces = result.get('spaces', [])
    
    if spaces:
        print(f"Found {len(spaces)} space(s):\n")
        for space in spaces:
            print(f"  📊 {space.get('space_id')}: {space.get('title')}")
            print(f"     Warehouse: {space.get('warehouse_id')}")
            print(f"     Description: {space.get('description', 'N/A')}")
            print()
    else:
        print("No spaces found")
        
except GenieSpaceError as e:
    print(f"❌ Error: {e.message}")
    if e.status_code == 501:
        print("Your workspace may not be enabled for the Genie API")
    elif e.status_code == 403:
        print("You may not have permission to access Genie Spaces")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Example 2: Get Space Details
# MAGIC
# MAGIC Retrieve detailed information about a specific space.

# COMMAND ----------

try:
    result = manager.list_spaces()
    spaces = result.get('spaces', [])
    
    if spaces:
        # Get the first space as an example
        space_id = spaces[0]['space_id']
        space = manager.get_space(space_id)
        
        print(f"Space Details:")
        print(f"  Title: {space.get('title')}")
        print(f"  Description: {space.get('description', 'N/A')}")
        print(f"  Space ID: {space.get('space_id')}")
        print(f"  Warehouse ID: {space.get('warehouse_id')}")
        print(f"  Created By: {space.get('created_by', 'N/A')}")
        print(f"  Created At: {space.get('created_at', 'N/A')}")
    else:
        print("No spaces available to query")
        
except GenieSpaceError as e:
    print(f"❌ Error: {e.message}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Example 3: Export Space Configuration
# MAGIC
# MAGIC Export a space with its full configuration for backup or migration.

# COMMAND ----------

try:
    result = manager.list_spaces()
    spaces = result.get('spaces', [])
    
    if spaces:
        space_id = spaces[0]['space_id']
        
        # Export with full configuration
        exported = manager.get_space(space_id, include_serialized_space=True)
        
        print(f"Exported space: {exported.get('title')}")
        print(f"Has serialized_space: {'serialized_space' in exported}")
        print(f"\nConfiguration keys: {list(exported.keys())}")
        
        # Optionally save to DBFS
        # dbutils.fs.put("/FileStore/genie_exports/exported_space.json", 
        #                json.dumps(exported, indent=2), 
        #                overwrite=True)
        # print("Saved to /FileStore/genie_exports/exported_space.json")
    else:
        print("No spaces available to export")
        
except GenieSpaceError as e:
    print(f"❌ Error: {e.message}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Example 4: Create a New Space
# MAGIC
# MAGIC Create a new Genie Space in your workspace.
# MAGIC
# MAGIC **⚠️ Note:** Update the parameters below with your actual values before running.

# COMMAND ----------

# Uncomment and update the values to create a space
"""
try:
    new_space = manager.create_space(
        warehouse_id="your_warehouse_id",  # Replace with your warehouse ID
        parent_path="/Workspace/Users/your.email@company.com/Genie Spaces",  # Replace with your path
        title="My New Genie Space",
        description="Created via databricks-genie-spaces package"
    )
    
    print(f"✅ Created space: {new_space['space_id']}")
    print(f"   Title: {new_space['title']}")
    print(f"   Warehouse: {new_space['warehouse_id']}")
    
except GenieSpaceError as e:
    print(f"❌ Error: {e.message}")
    if e.status_code == 400:
        print("Check that warehouse_id and parent_path are valid")
    elif e.status_code == 403:
        print("You may not have permission to create spaces at this path")
"""

# COMMAND ----------

# MAGIC %md
# MAGIC ## Example 5: Update an Existing Space
# MAGIC
# MAGIC Update the title or description of an existing space.
# MAGIC
# MAGIC **⚠️ Note:** Update the space_id before running.

# COMMAND ----------

# Uncomment and update the values to update a space
"""
try:
    manager.update_space(
        space_id="your_space_id",  # Replace with actual space ID
        title="Updated Space Title",
        description="Updated description via API"
    )
    
    print("✅ Space updated successfully")
    
except GenieSpaceError as e:
    print(f"❌ Error: {e.message}")
    if e.status_code == 404:
        print("Space not found - check the space_id")
    elif e.status_code == 403:
        print("You may not have permission to update this space")
"""

# COMMAND ----------

# MAGIC %md
# MAGIC ## Example 6: Delete (Trash) a Space
# MAGIC
# MAGIC Delete a Genie Space. This moves it to trash (may be recoverable).
# MAGIC
# MAGIC **⚠️ Warning:** This is a destructive operation!

# COMMAND ----------

# Uncomment and update the value to delete a space
"""
try:
    space_id = "your_space_id"  # Replace with actual space ID
    
    # Optional: Confirm before deletion
    confirm = input(f"Are you sure you want to delete space {space_id}? (yes/no): ")
    
    if confirm.lower() == "yes":
        manager.trash_space(space_id)
        print(f"✅ Space {space_id} has been trashed")
    else:
        print("Deletion cancelled")
    
except GenieSpaceError as e:
    print(f"❌ Error: {e.message}")
    if e.status_code == 404:
        print("Space not found or already deleted")
    elif e.status_code == 403:
        print("You may not have permission to delete this space")
"""

# COMMAND ----------

# MAGIC %md
# MAGIC ## Example 7: Query a Space (Use databricks-ai-bridge)
# MAGIC
# MAGIC For asking questions to Genie Spaces, use the `databricks-ai-bridge` package:

# COMMAND ----------

# Uncomment to query a Genie Space
"""
from databricks_ai_bridge.genie import GenieClient

# Initialize Genie client for a specific space
space_id = "your_space_id"  # Replace with your space ID
genie = GenieClient(w, space_id=space_id)

# Ask a question
response = genie.ask_question("What were total sales last quarter?")
print(response.result)

# Continue the conversation
response2 = genie.ask_question(
    "Break that down by region",
    conversation_id=response.conversation_id
)
print(response2.result)
"""

# COMMAND ----------

# MAGIC %md
# MAGIC ## Complete Workflow Example
# MAGIC
# MAGIC Putting it all together: Create → Query → Export → Update

# COMMAND ----------

# Complete workflow (uncomment and update values to run)
"""
try:
    # 1. Create a space
    new_space = manager.create_space(
        warehouse_id="abc123",
        parent_path="/Workspace/Users/user@example.com/Genie Spaces",
        title="Customer Analytics"
    )
    space_id = new_space['space_id']
    print(f"✅ Created space: {space_id}")
    
    # 2. Query the space (requires databricks-ai-bridge)
    from databricks_ai_bridge.genie import GenieClient
    genie = GenieClient(w, space_id=space_id)
    response = genie.ask_question("Show me top 10 customers by revenue")
    print(f"📊 Query result: {response.result}")
    
    # 3. Export configuration for backup
    exported = manager.get_space(space_id, include_serialized_space=True)
    dbutils.fs.put(
        f"/FileStore/backups/space_{space_id}.json", 
        json.dumps(exported, indent=2),
        overwrite=True
    )
    print(f"💾 Backed up to DBFS")
    
    # 4. Update space configuration
    manager.update_space(
        space_id,
        description="Updated analytics space with customer data"
    )
    print(f"✅ Updated space configuration")
    
except GenieSpaceError as e:
    print(f"❌ Error in workflow: {e.message}")
"""

# COMMAND ----------

# MAGIC %md
# MAGIC ## Error Handling Reference
# MAGIC
# MAGIC Common error codes you might encounter:
# MAGIC
# MAGIC | Code | Meaning | Common Cause |
# MAGIC |------|---------|--------------|
# MAGIC | 400 | Bad Request | Invalid parameters (check warehouse_id, parent_path) |
# MAGIC | 401 | Unauthorized | Invalid or expired authentication token |
# MAGIC | 403 | Forbidden | Insufficient permissions on space or parent path |
# MAGIC | 404 | Not Found | Space doesn't exist or was deleted |
# MAGIC | 501 | Not Implemented | Workspace not enabled for Genie API |
# MAGIC
# MAGIC ## Next Steps
# MAGIC
# MAGIC - Check out the full documentation: https://github.com/databricks/databricks-genie-spaces
# MAGIC - For querying spaces: https://github.com/databricks/databricks-ai-bridge
# MAGIC - Genie API docs: https://docs.databricks.com/api/workspace/genie


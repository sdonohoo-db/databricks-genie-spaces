"""
Basic usage examples for Databricks Genie Spaces Management

This demonstrates the CRUD operations for managing Genie Spaces.
For querying spaces, see databricks-ai-bridge.
"""

from databricks.sdk import WorkspaceClient
from databricks_genie_spaces import GenieSpacesManager, GenieSpaceError
import json


def main():
    # Initialize WorkspaceClient
    # This uses default authentication (environment variables or .databrickscfg)
    w = WorkspaceClient()
    
    # Create spaces manager
    manager = GenieSpacesManager(w)
    
    try:
        # Example 1: List all spaces
        print("=" * 60)
        print("Example 1: List all Genie Spaces")
        print("=" * 60)
        
        result = manager.list_spaces()
        spaces = result.get('spaces', [])
        
        if spaces:
            print(f"\nFound {len(spaces)} space(s):")
            for space in spaces:
                print(f"  - {space.get('space_id')}: {space.get('title')}")
                print(f"    Warehouse: {space.get('warehouse_id')}")
                print(f"    Description: {space.get('description', 'N/A')}")
        else:
            print("No spaces found")
        
        # Example 2: Get space details (if we have spaces)
        if spaces:
            print("\n" + "=" * 60)
            print("Example 2: Get space details")
            print("=" * 60)
            
            space_id = spaces[0]['space_id']
            space = manager.get_space(space_id)
            
            print(f"\nSpace: {space.get('title')}")
            print(f"Description: {space.get('description', 'N/A')}")
            print(f"Warehouse ID: {space.get('warehouse_id')}")
            print(f"Created By: {space.get('created_by', 'N/A')}")
        
        # Example 3: Export a space
        if spaces:
            print("\n" + "=" * 60)
            print("Example 3: Export space configuration")
            print("=" * 60)
            
            space_id = spaces[0]['space_id']
            exported = manager.get_space(space_id, include_serialized_space=True)
            
            print(f"\nExported space: {exported.get('title')}")
            print(f"Has serialized_space: {'serialized_space' in exported}")
            
            # Save to file
            filename = "exported_space.json"
            with open(filename, 'w') as f:
                json.dump(exported, f, indent=2)
            print(f"Saved to {filename}")
        
        # Example 4: Create a new space (commented out)
        print("\n" + "=" * 60)
        print("Example 4: Create space (commented out)")
        print("=" * 60)
        print("""
# To create a space:
new_space = manager.create_space(
    warehouse_id="your_warehouse_id",
    parent_path="/Workspace/Users/your.email@company.com/Genie Spaces",
    title="My New Space",
    description="Created via databricks-genie-spaces"
)
print(f"Created: {new_space['space_id']}")
        """)
        
        # Example 5: Update a space (commented out)
        print("\n" + "=" * 60)
        print("Example 5: Update space (commented out)")
        print("=" * 60)
        print("""
# To update a space:
manager.update_space(
    space_id="space_id_here",
    title="Updated Title",
    description="Updated description"
)
        """)
        
        # Example 6: Query a space using databricks-ai-bridge
        print("\n" + "=" * 60)
        print("Example 6: Query a space (use databricks-ai-bridge)")
        print("=" * 60)
        print("""
# For querying spaces, use databricks-ai-bridge:
from databricks_ai_bridge.genie import GenieClient

genie = GenieClient(w, space_id="your_space_id")
response = genie.ask_question("What were total sales last quarter?")
print(response.result)

# Continue conversation
response2 = genie.ask_question(
    "Break that down by region",
    conversation_id=response.conversation_id
)
print(response2.result)
        """)
        
    except GenieSpaceError as e:
        print(f"\n❌ Error: {e.message}")
        if e.status_code == 501:
            print("Your workspace may not be enabled for the Genie API")
        elif e.status_code == 403:
            print("You may not have permission to access Genie Spaces")


if __name__ == "__main__":
    main()

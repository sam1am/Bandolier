import asana
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the environment variables
access_token = os.getenv('ASANA_ACCESS_TOKEN')

# Instantiate the Asana client with the access token
client = asana.Client.access_token(access_token)

# List all available workspaces
def list_workspaces(client):
    workspaces = list(client.workspaces.find_all())
    print("Workspaces:")
    for workspace in workspaces:
        print(f"Workspace: {workspace['name']} (ID: {workspace['gid']})")
    return workspaces

# List all projects in a given workspace
def list_projects(client, workspace_id):
    projects = list(client.projects.find_by_workspace(workspace_id))
    print(f"Projects in workspace {workspace_id}:")
    for project in projects:
        print(f"Project: {project['name']} (ID: {project['gid']})")
    return projects

def main():
    try:
        # List workspaces
        workspaces = list_workspaces(client)
        
        # For demonstration purposes, we're selecting the first workspace
        selected_workspace_id = workspaces[0]['gid']
        
        # List projects
        list_projects(client, selected_workspace_id)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()

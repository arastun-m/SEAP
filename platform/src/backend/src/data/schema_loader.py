"""Loads Database Schema Details"""

import yaml
from config import SCHEMA_FILE


def load_schema():
    with open(SCHEMA_FILE, "r") as f:
        return yaml.safe_load(f)

def get_database_name():
    schema = load_schema()
    return schema.get("database", "default_database")
    
def get_container_data():
    """Returns a dictionary of container names and their partition keys."""
    schema = load_schema()
    container_data = {}
    for container in schema.get("containers", []):
        name = container["name"]
        partition_key = container.get("partition_key", "/id")
        container_data[name] = partition_key
    return container_data

def get_mock_data_file(container_name):
    schema = load_schema()
    for container in schema.get("containers", []):
        if container["name"] == container_name:
            return container.get("mock_data")
    return None


DATABASE_NAME = get_database_name()
CONTAINER_DATA = get_container_data() # CONTAINER DATA: dictionary of container names and their partition keys
MOCK_DATA_FILES = {
    container: get_mock_data_file(container) for container in CONTAINER_DATA.keys()
}

print(f"Database Name: {DATABASE_NAME}")
print(f"Container Data: {CONTAINER_DATA}")
print(f"Mock Data Files: {MOCK_DATA_FILES}")

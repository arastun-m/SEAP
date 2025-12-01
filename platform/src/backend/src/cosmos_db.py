"""Azure Cosmos DB client and database setup"""

import uuid
import json
import jsonref

from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient, PartitionKey, exceptions

import config


class CosmosDBClient:
    """
    A class to manage the Azure Cosmos DB client and database operations.
    """

    def __init__(self):
        # initalize the Cosmos client with key-based authentication
        key = config.AZURE_COSMOSDB_KEY
        endpoint = config.AZURE_COSMOSDB_ENDPOINT
        self.client = CosmosClient(endpoint, {'masterKey': key})
        print("Cosmos client initialized")

        # database and container setup (meta-data)
        self.database_name = "campus"
        # connect to the database and get containers
        self.database_proxy, self.containers_proxy = self.connect_database()

    # ----------------- Connecting to the DB, Defining DATABASE and CONTAINERS -----------------
    def connect_database(self):
        database_proxy = None
        containers_proxy = {}

        try:
            database_proxy = self.client.get_database_client(self.database_name)
            containers = database_proxy.list_containers()
            for cont in containers: # get all of the available containers
                containers_proxy[cont["id"]] = database_proxy.get_container_client(cont["id"])
            # print available containers
            print(f"Available containers in {self.database_name}: {[key for key in containers_proxy.keys()]}\n")

        except exceptions.CosmosHttpResponseError as e:
            print(f"Database connection failed: {e}")
        return database_proxy, containers_proxy

    # ----------------- Creating Containers & Adding Data -----------------
    def create_container(self, container_name, partition_key):
        """
        Creates a new container in the database with the specified partition key.
        """
        try:
            container = self.database_proxy.create_container_if_not_exists(
                id=container_name,
                partition_key=PartitionKey(path=partition_key)
            )
            self.containers_proxy[container_name] = container
            print(f"Container '{container_name}' created successfully.")
        except exceptions.CosmosResourceExistsError:
            print(f"Container '{container_name}' already exists.")
        except exceptions.CosmosHttpResponseError as e:
            print(f"Failed to create container '{container_name}': {e}")

    def add_mock_data(self, container_name, mock_data_file, count=1):
        """
        Adds mock data to the specified container from the corresponding JSON file.
        CONTAINER_DATA and MOCK_DATA_FILES are defined in schema_loader.py.
        """

        if container_name not in self.containers_proxy:
            print(f"Container '{container_name}' does not exist.")
            return
        if not mock_data_file:
            print(f"No mock data file defined for container '{container_name}'.")
            return

        container = self.containers_proxy.get(container_name)
        mock_data_file = f"{config.MOCK_DATA_DIR}/{mock_data_file}"
        try:
            with open(mock_data_file, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to load {mock_data_file}: {e}")
            return

        count = min(count, len(data)) # limit base on available data
        for i in range(count):
            item = data[i]

            try:
                container.create_item(body=item)
                print(f"Added item {i+1}/{count} to container '{container_name}'.")
            except exceptions.CosmosResourceExistsError:
                print(f"Item with id {item["id"]} already exists in container '{container_name}'.")
            except exceptions.CosmosHttpResponseError as e:
                print(f"Failed to add item {item["id"]} to container '{container_name}': {e}")

    # ----------------- Preview -----------------
    def get_table(self, container_name):
        """
        Returns all items in the specified container.
        """
        if container_name not in self.containers_proxy:
            print(f"Container '{container_name}' does not exist.")
            return []
        container = self.containers_proxy.get(container_name)
        items = container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        )
        
        # cleanup items by removing metadata fields
        items = list(items)
        for item in items:
            item.pop("_rid", None)
            item.pop("_self", None)
            item.pop("_etag", None)
            item.pop("_attachments", None)
            item.pop("_ts", None)
        return items


def test_run():
    # example usage
    cosmos_client = CosmosDBClient()
    # adding mock data
    # cosmos_client.create_container("users", "/id")
    # cosmos_client.add_mock_data("users", "users.json", count=11)
    # print(cosmos_client.get_table("users"))
    container_name = "energy_feedback"
    #cosmos_client.create_container(container_name, "/id")
    #cosmos_client.add_mock_data(container_name, f"{container_name}.json", count=100)
    print(cosmos_client.get_table(container_name))


if __name__ == "__main__":
    test_run()

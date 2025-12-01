"""
Specialised Agent: Campus General Information 

Dynamic Prompt Augmentation (Lightweight RAG)
1. Each tools returns a database container (selected by the agent)
2. Content is dumped into a prompt template
"""

from typing import Any, Callable, Set, Dict, List, Optional
from typing_extensions import Annotated

from semantic_kernel.functions import kernel_function

from cosmos_db import CosmosDBClient


class CampusInfoPlugin:
    """Campus General Information Plugin"""

    def __init__(self, cosmos_client: CosmosDBClient):
        self.cosmos_client = cosmos_client

    @kernel_function
    def get_containers(self) -> Annotated[list[str], "List of available Cosmos DB containers"]:
        """
        Retrieves a list of all available Cosmos DB containers in the database.
        """
        try:
            return list(self.cosmos_client.containers_proxy.keys())
        except Exception as e:
            return ["Error retrieving containers. Please check your request and try again."] + str(e)

    @kernel_function
    def get_data(self, container_name: str) -> Annotated[str, "All data from the specified container"]:
        """
        Retrieves all data available in the specified Cosmos DB container.

        Parameters:
            container_name: The name of the Cosmos DB container to retrieve data from.
        """

        try:
            if container_name not in self.cosmos_client.containers_proxy:
                return f"Container '{container_name}' does not exist. Available containers: {', '.join(self.cosmos_client.containers_proxy.keys())}"
            return self.cosmos_client.get_table(container_name)
        except Exception as e:
            return "Error retrieving data from the container. Please check your request and try again." + str(e)

    @staticmethod
    def get_all_tools_definitions() -> List[dict]:
        return [
            {
                "id": "get_containers",
                "name": "get_containers",
                "description": "Retrieves a list of all available Cosmos DB containers.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "id": "get_data",
                "name": "get_data",
                "description": "Retrieves all data from the specified Cosmos DB container.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_name": {
                            "type": "string",
                            "description": "The name of the Cosmos DB container to retrieve data from."
                        }
                    },
                    "required": ["container_name"]
                }
            }
        ]


def get_ai_agent_tools():
    """ Azure AI Agent toolset """
    plugin = CampusInfoPlugin()
    user_functions: Set[Callable[..., Any]]  = {
        plugin.get_containers,
        plugin.get_data,
    }
    return user_functions

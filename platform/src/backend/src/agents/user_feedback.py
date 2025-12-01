"""
Specalised Agent: Used Feedback Collector
Aimed to collect feedback from users (students, staff, faculty) about the rooms they use.
"""

from typing_extensions import Annotated, List, Literal
import datetime
import uuid

from semantic_kernel.functions import kernel_function

from cosmos_db import CosmosDBClient


class UserFeedbackPlugin:
    """User Feedback Collector Plugin"""
    def __init__(self, cosmos_client: CosmosDBClient):
        self.cosmos_client = cosmos_client

    # ============================================== FEEDBACK PRE-PROCESSING AND COLLECTION ==============================================
    @kernel_function
    def validate_room(self, room_name: Annotated[str, "e.g., Lecture Theatre 1, Meeting Room 1"]) -> \
            Annotated[str, "Returns room_id if the room exists, an error message if the room does not exist."]:
        """
        Validates if the specified room exists in the database.

        Parameters:
            room_name: The name of the room to validate.
        """

        room_container_name = "rooms"  # Assuming 'rooms' is the container where room data is stored
        try:
            room_data =  self.cosmos_client.get_table(room_container_name)
            room_data = [(room["id"], room["name"]) for room in room_data]  # Assuming each room has a 'name' field
            for (id, name) in room_data:
                if name.lower() == room_name.lower():
                    return f"Room '{name}' exists with ID '{id}'."
            return f"Room '{room_name}' does not exist in the system. Available rooms are '{room_data}."
        
        except Exception as e:
            return "Error retrieving data from the container. Please check your request and try again." + str(e)

    @kernel_function
    def register_feedback(self, user_id: Annotated[str, "e.g., user_001, user_002"],
                                room_id: Annotated[str, "e.g., LT1, MR01"],
                                category: Literal["Temperature", "Lighting", "Air", "Other"],
                                feedback_message: str) -> Annotated[str, "Confirmation message"]:
        """
        Register the user feedback into the system and send a confirmation message.

        Parameters:
            user_id: The ID of the user providing the feedback.
            room_id: The ID of the room assigned to the feedback.
            feedback_message: The content of the feedback.
            category: The category of the feedback
        """
        feedback_info = {
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "user_id": user_id,
            "feedback": feedback_message,
            "category": category,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        # store it in the database 
        res = self.store_energy_feedback(feedback_info)
        # confirmation message
        return f'feedback_info stored successfully: {feedback_info}' if res else 'Failed to store feedback information'
    
    # ============================================== DATABASE ACCESS FUNCTIONS ==============================================
    def store_energy_feedback(self, feedback_info: dict) -> bool:
        """
        Helper function to store the energy feedback information in the Cosmos DB.
        
        Parameters:
            feedback_info: A dictionary containing the feedback information.
        Returns:
            bool: True if the feedback was stored successfully, False otherwise.
        """
        try:
            container_name = "energy_feedback" # assuming container name
            if container_name not in self.cosmos_client.containers_proxy:
                self.cosmos_client.create_container(container_name, "/id")
            container = self.cosmos_client.containers_proxy.get(container_name)
            container.create_item(body=feedback_info)
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def get_all_tools_definitions() -> List[dict]:
        return [
            {
                "id": "validate_room",
                "name": "validate_room",
                "description": "Validates if the specified room exists in the database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room_name": {
                            "type": "string",
                            "description": "The name of the room to validate."
                        }
                    },
                    "required": ["room_name"]
                }
            },
            {
                "id": "register_feedback",
                "name": "register_feedback",
                "description": "Registers the user feedback into the system and sends a confirmation message.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user providing the feedback."
                        },
                        "room_id": {
                            "type": "string",
                            "description": "The id of the room assigned to the feedback."
                        },
                        "feedback_message": {
                            "type": "string",
                            "description": "The content of the feedback."
                        },
                        "category": {
                            "type": "string",
                            "description": "The category of the feedback (e.g., room temperature, lighting)."
                        }
                    },
                    "required": ["user_id", "room_id", "feedback_message", "category"]
                }
            }
        ]
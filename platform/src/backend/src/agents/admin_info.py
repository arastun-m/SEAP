"""
Specalised Agent: AdminInfo
Admin-level information access and high-level analysis
"""

from datetime import datetime
import numpy as np
from typing_extensions import Annotated

from semantic_kernel.functions import kernel_function

from cosmos_db import CosmosDBClient


class AdminInfoPlugin:
    """Admin Info Plugin
    """

    def __init__(self, cosmos_client: CosmosDBClient):
        self.cosmos_client = cosmos_client

    # ============================================== INFORMATION RETRIEVAL FUNCTIONS ==============================================
    @kernel_function
    def get_user_info(self) -> Annotated[list[str], "List of all registered users"]:
        """
        Retrieves a list of all registered users in the system.
        Only use this if you want general user information.
        """
        return self.get_data("users")
    
    @kernel_function
    def get_infrastructure(self) -> Annotated[dict, "Metadata on buildings, rooms, HVAC zones"]:
        """
        Retrieves fully detailed metadata on buildings, HVAC zones, and rooms.
        """
        try:
            infrastructure_data = {
                "buildings": self.get_data("building"),
                "rooms": self.get_data("rooms"),
                "hvac_zones": self.get_data("hvac_zone")
            }
            return infrastructure_data
        except Exception as e:
            return "Error retrieving infrastructure data. Please check your request and try again." + str(e)
    
    @kernel_function
    def get_room_id(self, room_name: str) -> Annotated[str, "Room ID for the given room name if it exists"]:
        """
        Retrieves the room ID for a given room name.
        Parameters:
            room_name: The name of the room to retrieve the ID for.
        """
        container_name = "rooms"
        try:
            if container_name not in self.cosmos_client.containers_proxy:
                return f"Container '{container_name}' does not exist. Available containers: {', '.join(self.cosmos_client.containers_proxy.keys())}"
            container = self.cosmos_client.containers_proxy.get(container_name)
            sql_query = f"SELECT c.id FROM c WHERE c.name = @room_name"
            parameters = [{"name": "@room_name", "value": room_name}]
            room_ids = list(container.query_items(
                query=sql_query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            if room_ids:
                return room_ids[0]["id"]
            else:
                return f"No room found with name: {room_name} available rooms:\
                    {', '.join([room['room_name'] for room in self.get_data('rooms')])}"
        except Exception as e:
            return "Error retrieving room ID. Please check your request and try again." + str(e)
    
    @kernel_function
    def get_hvac_zone_id(self, zone_name: str) -> Annotated[str, "HVAC Zone ID for the given zone name if it exists"]:
        """
        Retrieves the HVAC zone ID for a given zone name.
        Parameters:
            zone_name: The name of the HVAC zone to retrieve the ID for.
        """
        container_name = "hvac_zone"
        try:
            if container_name not in self.cosmos_client.containers_proxy:
                return f"Container '{container_name}' does not exist. Available containers: {', '.join(self.cosmos_client.containers_proxy.keys())}"
            container = self.cosmos_client.containers_proxy.get(container_name)
            sql_query = f"SELECT c.id FROM c WHERE c.zone_name = @zone_name"
            parameters = [{"name": "@zone_name", "value": zone_name}]
            zone_ids = list(container.query_items(
                query=sql_query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            if zone_ids:
                return zone_ids[0]["id"]
            else:
                return f"No HVAC zone found with name: {zone_name} available zones:\
                    {', '.join([zone['zone_name'] for zone in self.get_data('hvac_zone')])}"
        except Exception as e:
            return "Error retrieving HVAC zone ID. Please check your request and try again." + str(e)
    
    @kernel_function
    def get_building_id(self, building_name: str) -> Annotated[str, "Building ID for the given building name if it exists"]:
        """
        Retrieves the building ID for a given building name.
        Parameters:
            building_name: The name of the building to retrieve the ID for.
        """
        container_name = "building"
        try:
            if container_name not in self.cosmos_client.containers_proxy:
                return f"Container '{container_name}' does not exist. Available containers: {', '.join(self.cosmos_client.containers_proxy.keys())}"
            container = self.cosmos_client.containers_proxy.get(container_name)
            sql_query = f"SELECT c.id FROM c WHERE c.building_name = @building_name"
            parameters = [{"name": "@building_name", "value": building_name}]
            building_ids = list(container.query_items(
                query=sql_query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            if building_ids:
                return building_ids[0]["id"]
            else:
                return f"No building found with name: {building_name} available buildings:\
                    {', '.join([building['building_name'] for building in self.get_data('building')])}"
        except Exception as e:
            return "Error retrieving building ID. Please check your request and try again." + str(e)

    @kernel_function
    def get_room_status(self, room_id: Annotated[str, "e.g., LT1, FW26"]) ->\
            Annotated[dict | str, "Room status data with timestamps and paired values (temperature, co2, occupancy), or error message"]:
        """
        Retrieves archived status of a specific room.
        Parameters:
            room_id: The ID of the room to retrieve status from.
        """
        timestamp_paired_values = self.get_room_status_data(room_id)
        return timestamp_paired_values if timestamp_paired_values else f"No status data found for room: {room_id}"
    
    @kernel_function
    def get_energy_metrics(self, zone_id: Annotated[str, "e.g., zone_lecture, zone_office"]) ->\
            Annotated[dict, "Energy metrics data with timestamps and paired values (usage, cost, cost breakdown), or error message"]:
        """
        Retrieves archived energy metrics of a specific HVAC zone.
        Parameters:
            zone_id: The ID of the HVAC zone to retrieve metrics from.
        """
        timestamp_paired_values = self.get_hvac_action_data(zone_id)
        return timestamp_paired_values if timestamp_paired_values else f"No action data found for zone: {zone_id}"

    # ============================================== DATABASE ACCESS FUNCTIONS ==============================================
    def get_room_status_data(self, room_id: Annotated[str, "e.g., LT1, FW25"]) ->\
            Annotated[dict | str, "Room status data with timestamps and paired values (temperature, co2, occupancy), or error message"]:
        """
        Returns sorted (recent first) timestamps with paried values (temperature, co2, occupancy) for a given room.
        Returns an error message if the room does not exist.
        """
        container_name = "room_status"
        try: # retrieve data
            if container_name not in self.cosmos_client.containers_proxy:
                return f"Container '{container_name}' does not exist. Available containers: \
                    {', '.join(self.cosmos_client.containers_proxy.keys())}"
            container = self.cosmos_client.containers_proxy.get(container_name)
            sql_query = f"SELECT c.current_temperature, c.current_co2, c.occupants, c.timestamp FROM c WHERE c.room_id = @room_id"
            parameters = [{"name": "@room_id", "value": room_id}]
            status_data = list(container.query_items(
                query=sql_query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
        except Exception as e:
            return "Error retrieving data from the container. Please check your request and try again." + str(e)
    
        # reformat data: pair timestamps with values (temperature, co2, occupancy)
        if not status_data: return {}
        timestamp_paired_values = {}
        for data in status_data:
            timestamp_paired_values[datetime.fromisoformat(data["timestamp"])] = {
                "temperature": data["current_temperature"],
                "co2": data["current_co2"],
                "occupancy": data["occupants"]
            }
        # sort based on timestamps (most recent first) while keeping the paired values
        sorted_timestamps = sorted(timestamp_paired_values.keys(), reverse=True)
        timestamp_paired_values = {
            timestamp: timestamp_paired_values[timestamp] for timestamp in sorted_timestamps
        }
        return timestamp_paired_values

    def get_hvac_action_data(self, zone_id: Annotated[str, "e.g., zone_lecture, zone_office"]) ->\
            Annotated[dict | str, "HVAC zone action data with timestamps and paired values (usage, cost, cost breakdown), or error message"]:
        """
        Returns sorted (recent first) timestamps with paired values (usage, cost, cost breakdown) for a given HVAC zone.
        Returns an error message if the zone does not exist.
        """
        container_name = "hvac_action"
        try: # retrieve data
            if container_name not in self.cosmos_client.containers_proxy:
                return f"Container '{container_name}' does not exist. Available containers: \
                    {', '.join(self.cosmos_client.containers_proxy.keys())}"
            container = self.cosmos_client.containers_proxy.get(container_name)
            sql_query = f"SELECT c.total_energy_kwh, c.total_cost_pounds, c.cost_breakdown, c.timestamp FROM c WHERE c.zone_id = @zone_id"
            parameters = [{"name": "@zone_id", "value": zone_id}]
            action_data = list(container.query_items(
                query=sql_query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
        except Exception as e:
            return "Error retrieving data from the container. Please check your request and try again." + str(e)
        
        # reformat data: pair timestamps with values (usage, cost, cost breakdown)
        if not action_data: return {}
        timestamp_paired_values = {}
        for data in action_data:
            timestamp_paired_values[datetime.fromisoformat(data["timestamp"])] = {
                "usage": data["total_energy_kwh"],
                "cost": data["total_cost_pounds"],
                "cost_breakdown": data["cost_breakdown"]
            }
        # sort based on timestamps (most recent first) while keeping the paired values
        sorted_timestamps = sorted(timestamp_paired_values.keys(), reverse=True)
        timestamp_paired_values = {
            timestamp: timestamp_paired_values[timestamp] for timestamp in sorted_timestamps
        }
        return timestamp_paired_values

    def get_containers(self) -> Annotated[list[str], "List of available Cosmos DB containers"]:
        """
        Retrieves a list of all available Cosmos DB containers in the database.
        """
        try:
            return list(self.cosmos_client.containers_proxy.keys())
        except Exception as e:
            return ["Error retrieving containers. Please check your request and try again."] + str(e)

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
    def get_all_tools_definitions() -> list[dict]:
        return [
            {
                "name": "get_user_info",
                "description": "Retrieves a list of all registered users in the system.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_user_roles",
                "description": "Retrieves a list of all available user roles.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_infrastructure",
                "description": "Retrieves metadata on buildings, rooms, and HVAC zones.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_room_status",
                "description": "Retrieves live/archived status of a specific room.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room_name": {
                            "type": "string",
                            "description": "The name of the room to retrieve status for."
                        }
                    },
                    "required": ["room_name"]
                }
            }
        ]
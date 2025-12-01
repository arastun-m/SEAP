"""
Specialised Agent: ChartPlotter
Used to generate admin-level visual charts.

Supported Charts:
1. Room Status Charts: Temperature, CO2 and Occupancy trends in a specific room, HVAC zone or building.
2. Energy Metrics Charts: Energy consumption and cost trends for a specific HVAC zone or building.
3. Energy Cost Breakdown Charts: Detailed breakdown of energy costs for a specific HVAC zone or building
4. User Feedback Breadown Charts: User feedback trends for a specific room, HVAC zone or building.
"""

import uuid
import os
from datetime import datetime
import numpy as np
from typing_extensions import Annotated, Literal
import matplotlib.pyplot as plt
from numpy.random import default_rng as rng

from semantic_kernel.functions import kernel_function

from cosmos_db import CosmosDBClient


class ChartPlotterPlugin:
    """Chart Plotter Plugin"""
    def __init__(self, cosmos_client: CosmosDBClient):
        self.save_charts = True # control for evaluations
        self.dir = os.path.dirname(os.path.abspath(__file__)) # directory of current file
        self.directory = os.path.join(self.dir, "../charts/")
        self.cosmos_client = cosmos_client

    # ============================================== CHART GENERATION FUNCTIONS ==============================================
    @kernel_function
    def plot_room_status(self, room_id: Annotated[str, "e.g., LT1, FW26"], chart_type: Literal["temperature", "c02", "occupancy"]) ->\
            Annotated[str, "File path to the generated room status chart"]:
        """
        Generates a room status chart (temperature, CO2, or occupancy) for a specific room.
        :param room_id: ID of the room to generate the chart for.
        :param chart_type: Type of chart to generate ('temperature', 'co2', 'occupancy').
        """
        chart_name_pref = f"{self.directory}room_status_{room_id}_{chart_type}"
        chart_filepath = chart_name_pref + uuid.uuid4().hex + ".png"

        # plot and save the chart
        result = self.get_room_status_data(room_id, chart_type)
        if isinstance(result, str): return result # error message
        fixed_timestamps, status_values = result
        fig, ax = plt.subplots()
        ax.plot(fixed_timestamps, status_values, marker='o')
        ax.set_title(f"{chart_type.capitalize()} Trend in Room {room_id}")
        ax.set_xlabel("Time")
        ax.tick_params(axis='x', labelrotation=90)
        ax.set_ylabel(chart_type.capitalize())
        fig.autofmt_xdate()
        if self.save_charts: plt.savefig(chart_filepath)
        return chart_filepath

    @kernel_function
    def plot_zone_status(self, zone_id: Annotated[str, "e.g., zone_lecture, zone_office"], chart_type: Literal["temperature", "c02", "occupancy"]) ->\
            Annotated[str, "File path to the generated HVAC status chart"]:
        """
        Generates a HVAC zone status chart (temperature, CO2, or occupancy) for a specific HVAC zone.
        :param zone_id: ID of the HVAC zone to generate the chart for.
        :param chart_type: Type of chart to generate ('temperature', 'co2', 'occupancy').
        """
        rooms = self.get_data("rooms")
        if not isinstance(rooms, list): return rooms # error message
        room_ids = [room["id"] for room in rooms if room["zone_id"] == zone_id]
        if not room_ids: return f"No rooms found for HVAC zone '{zone_id}'."

        chart_name_pref = f"{self.directory}zone_status_{zone_id}_{chart_type}"
        chart_filepath = chart_name_pref + uuid.uuid4().hex + ".png"

        # stacked area plot: for each room combine the values and plot
        fig, ax = plt.subplots()
        status_values_per_room = []
        labels_per_room = []
        for room_id in room_ids:
            result = self.get_room_status_data(room_id, chart_type)
            if isinstance(result, str): return result
            if len(result[0]) == 0: continue  # skip if no data
            fixed_timestamps, status_values = result
            status_values_per_room.append(status_values)
            labels_per_room.append(room_id)
        labels_per_room = labels_per_room[:len(status_values_per_room)]  # adjust labels to match available data

        if not status_values_per_room:
            return f"No data found for HVAC zone '{zone_id}' with chart type '{chart_type}'"
        plt.stackplot(fixed_timestamps, *status_values_per_room, labels=labels_per_room)
        ax.set_title(f"{chart_type.capitalize()} Trend in HVAC Zone {zone_id}")
        ax.set_xlabel("Time")
        ax.tick_params(axis='x', labelrotation=45)
        ax.set_ylabel(chart_type.capitalize())
        ax.legend()
        fig.autofmt_xdate()
        if self.save_charts: plt.savefig(chart_filepath)
        return chart_filepath

    @kernel_function
    def plot_building_status(self, building_id: Annotated[str, "e.g., Engineering Building, Sports Buildinh"], chart_type: Literal["temperature", "c02", "occupancy"]) ->\
            Annotated[str, "File path to the generated building status chart"]:
        """
        Generates a building status chart (temperature, CO2, or occupancy) for a specific building
        :param building_id: ID of the building to generate the chart for.
        :param chart_type: Type of chart to generate ('temperature', 'co2', 'occupancy').
        """

        rooms = self.get_data("rooms")
        if not isinstance(rooms, list): return rooms # error message
        room_ids = [room["id"] for room in rooms if room["building_id"] == building_id]
        if not room_ids: return f"No rooms found for building '{building_id}'"

        chart_name_pref = f"{self.directory}building_status_{building_id}_{chart_type}"
        chart_filepath = chart_name_pref + uuid.uuid4().hex + ".png"

        # stacked area plot: for each room combine the values and plot
        fig, ax = plt.subplots()
        status_values_per_room = []
        labels_per_room = []
        for room_id in room_ids:
            result = self.get_room_status_data(room_id, chart_type)
            if isinstance(result, str): return result
            if len(result[0]) == 0: continue  # skip if no data
            fixed_timestamps, status_values = result
            status_values_per_room.append(status_values)
            labels_per_room.append(room_id)
        labels_per_room = labels_per_room[:len(status_values_per_room)]  # adjust labels to match available data

        if not status_values_per_room:
            return f"No data found for building '{building_id}' with chart type '{chart_type}'"
        plt.stackplot(fixed_timestamps, *status_values_per_room, labels=labels_per_room)
        ax.set_title(f"{chart_type.capitalize()} Trend in Building {building_id}")
        ax.set_xlabel("Time")
        ax.tick_params(axis='x', labelrotation=90)
        ax.set_ylabel(chart_type.capitalize())
        ax.legend()
        fig.autofmt_xdate()
        if self.save_charts: plt.savefig(chart_filepath)
        return chart_filepath
    
    @kernel_function
    def plot_zone_metrics(self, zone_id: Annotated[str, "e.g., zone_lecture, zone_office"], metric_type: Literal["usage", "cost", "cost breakdown"]) ->\
            Annotated[str, "File path to the generated zone metrics chart"]:
        """
        Suitable for charts on energy consumption/usage, costs, or cost breakdown for a specific HVAC zone.
        Generates a zone metrics chart (usage, cost, or cost breakdown) for a specific HVAC zone.
        :param zone_id: ID of the HVAC zone to generate the chart for.
        :param metric_type: Type of chart to generate ('usage', 'cost', 'cost breakdown').
        """

        chart_name_pref = f"{self.directory}zone_metrics_{zone_id}_{metric_type}"
        chart_filepath = chart_name_pref + uuid.uuid4().hex + ".png"

        # plot and save the chart
        result = self.get_hvac_action_data(zone_id, metric_type)
        if isinstance(result, str): return result  # error message
        if len(result[0]) == 0: return f"No data found for HVAC zone '{zone_id}' with metric type '{metric_type}'"
        fixed_timestamps, action_values = result
        fig, ax = plt.subplots()
        if metric_type == "cost breakdown": # stacked area plot for cost breakdown
            action_values = self.reformat_cost_breakdown(action_values)
            labels = list(action_values.keys())
            values = [action_values[label] for label in labels]
            plt.stackplot(fixed_timestamps, *values, labels=labels)
            ax.legend(loc='upper left')
        else:
            ax.plot(fixed_timestamps, action_values, marker='o')

        ax.set_title(f"{metric_type.capitalize()} Trend in HVAC Zone {zone_id}")
        ax.set_xlabel("Time")
        ax.set_ylabel(metric_type.capitalize())
        fig.autofmt_xdate()
        if self.save_charts: plt.savefig(chart_filepath)
        return chart_filepath

    @kernel_function
    def plot_building_metrics(self, building_id: Annotated[str, "e.g., Engineering Building, Sports Building"], metric_type: Literal["usage", "cost", "cost breakdown"]) ->\
            Annotated[str, "File path to the generated building metrics chart"]:
        """
        Generates a building metrics chart (usage, cost, or cost breakdown) for a specific building.
        It returns seperate charts for each zone in the building.
        :param building_id: ID of the building to generate the chart for.
        :param metric_type: Type of chart to generate ('usage', 'cost', 'cost breakdown').
        """
        zones = self.get_data("hvac_zone")
        if not isinstance(zones, list): return zones # error message
        zone_ids = [zone["id"] for zone in zones if zone["building_id"] == building_id]
        if not zone_ids: return f"No zones found for building '{building_id}'"

        # return multiple charts for each zone
        chart_filepaths = []
        for zone_id in zone_ids:
            chart_filepath = self.plot_zone_metrics(zone_id, metric_type)
            # is a chart if the path strats with chart/
            if chart_filepath.startswith(self.directory):
                chart_filepaths.append(chart_filepath)
        return chart_filepaths if chart_filepaths else f"No data found for building '{building_id}' with metric type '{metric_type}'"

    @kernel_function
    def plot_user_feedback(self,
        room_id: Annotated[str | None, "Room ID (e.g., LT1, FW26). Default None = no filter"] = None,
        user_id: Annotated[str | None, "User ID (e.g., user_001). Default None = no filter"] = None,
        category: Annotated[Literal["Temperature", "Lighting", "Air", "Other"] | None, "Feedback category. Default None = no filter"] = None,
    ) -> Annotated[str, "File path to the generated user feedback chart, or 'ERROR: ...' message"]:
        """
        Generates a user feedback chart based on optional filters (room, user, category).
        If no filters are provided, all feedback is included.
        """
        chart_name_pref = f"{self.directory}user_feedback_{room_id or 'all'}_{user_id or 'all'}_{category or 'all'}"
        chart_filepath = chart_name_pref + uuid.uuid4().hex + ".png"

        # retrieve feedback data
        feedback_data = self.get_feedback_data(room_id=room_id, user_id=user_id, category=category)
        if isinstance(feedback_data, str): return feedback_data  # error message
        if not feedback_data: return f"No feedback data found for room '{room_id}', user '{user_id}', or category '{category}'"

        # plot and save the chart
        # pie chart by category
        categories = [data["category"] for data in feedback_data]
        category_counts = {category: categories.count(category) for category in set(categories)}
        fig, ax = plt.subplots()
        ax.pie(category_counts.values(), labels=category_counts.keys(), autopct='%1.1f%%', startangle=90)
        ax.set_title(f"User Feedback Breakdown\nRoom: {room_id or 'All'}, User: {user_id or 'All'}, Category: {category or 'All'}")
        if self.save_charts: plt.savefig(chart_filepath)
        return chart_filepath

    # ============================================== DATA RETRIEVAL FUNCTIONS ==============================================
    def get_room_status_data(self, room_id: Annotated[str, "e.g., LT1, FW26"], data_type: Literal["temperature", "co2", "occupancy"]) ->\
            Annotated[tuple, "data values in specified data type along with timestamps"]:
        container_name = "room_status"
        status_val = {
            "temperature": "current_temperature",
            "co2": "current_co2",
            "occupancy": "occupants"
        }.get(data_type, None) # status value map from chart type to status field

        try: # retrieve data
            if container_name not in self.cosmos_client.containers_proxy:
                return f"Container '{container_name}' does not exist. Available containers: \
                    {', '.join(self.cosmos_client.containers_proxy.keys())}"
            container = self.cosmos_client.containers_proxy.get(container_name)
            sql_query = f"SELECT c.{status_val}, c.timestamp FROM c WHERE c.room_id = @room_id"
            parameters = [{"name": "@room_id", "value": room_id}]
            status_data = list(container.query_items(
                query=sql_query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
        except Exception as e:
            return "Error retrieving data from the container. Please check your request and try again." + str(e)

        # re-format the data to ensure consistent timestamps
        if not status_data: return [], []
        step = np.timedelta64(15, 'm') # 15-minute steps
        timestamps = [datetime.fromisoformat(data["timestamp"]) for data in status_data]
        timestamps_np = np.array(timestamps, dtype='datetime64[ns]')
        fixed_timestamps = np.arange(timestamps_np.min(), timestamps_np.max()+step, step=step, dtype='datetime64[m]')
        status_values = [data[status_val] for data in status_data]
        return fixed_timestamps, status_values
    
    def get_hvac_action_data(self, zone_id: Annotated[str, "e.g., zone_lecture, zone_office"], data_type: Literal["usage, cost, cost breakdown"]) ->\
            Annotated[tuple, "data values in specified data type along with timestamps"]:
        container_name = "hvac_action"
        action_val = {
            "usage": "total_energy_kwh",
            "cost": "total_cost_pounds",
            "cost breakdown": "cost_breakdown"
        }.get(data_type, None) # status value map from chart type to status field

        try: # retrieve data
            if container_name not in self.cosmos_client.containers_proxy:
                return f"Container '{container_name}' does not exist. Available containers: \
                    {', '.join(self.cosmos_client.containers_proxy.keys())}"
            container = self.cosmos_client.containers_proxy.get(container_name)
            sql_query = f"SELECT c.{action_val}, c.timestamp FROM c WHERE c.zone_id = @zone_id"
            parameters = [{"name": "@zone_id", "value": zone_id}]
            action_data = list(container.query_items(
                query=sql_query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
        except Exception as e:
            return "Error retrieving data from the container. Please check your request and try again." + str(e)

        # re-format the data to ensure consistent timestamps
        if not action_data: return [], []
        step = np.timedelta64(15, 'm') # 15-minute steps
        timestamps = [datetime.fromisoformat(data["timestamp"]) for data in action_data]
        timestamps_np = np.array(timestamps, dtype='datetime64[ns]')
        fixed_timestamps = np.arange(timestamps_np.min(), timestamps_np.max()+step, step=step, dtype='datetime64[m]')
        action_values = [data[action_val] for data in action_data]
        return fixed_timestamps, action_values
    
    def get_feedback_data(self, room_id=None, user_id=None, category=None) ->\
            Annotated[list | str, "Filtered energy feedback data or an error message"]:
        """
        Retrieves energy feedback data.
        Filters the data based on room_id, user_id, and category if provided.
        Sorts the data by timestamp in descending order (most recent first).
        
        Parameters:
            room_id: Optional; filter by specific room ID.
            user_id: Optional; filter by specific user ID.
            category: Optional; filter by specific feedback category.
        Returns:
            list: Filtered feedback data.
            str: Error message if the container does not exist or if an error occurs.
        """
        container_name = "energy_feedback"
        feedback_data = self.get_data(container_name)  # check if the container exists
        if not isinstance(feedback_data, list): return feedback_data
        if not feedback_data: return []

        # filter data based on parameters (if provided)
        if room_id:
            feedback_data = [data for data in feedback_data if data["room_id"] == room_id]
        if user_id:
            feedback_data = [data for data in feedback_data if data["user_id"] == user_id]
        if category:
            feedback_data = [data for data in feedback_data if data["category"] == category]

        # reformat the timestamp based on datetime.isoformat and sort by timestamp (by recent first)
        feedback_data = sorted(feedback_data, key=lambda x: datetime.fromisoformat(x["timestamp"]), reverse=True)
        return feedback_data

    def reformat_cost_breakdown(self, cost_breakdown: list) -> Annotated[dict[list], "Reformatted cost breakdown data"]:
        """
        Reformat ['Heating £0.051 | Cooling £0.012 | Ventilation £0.039', 'Heating £0.088 | Cooling £0.021 | Ventilation £0.067']
        to {'Heating': [0.051, 0.088], 'Cooling': [0.012, 0.021], 'Ventilation': [0.039, 0.067]}
        """

        breakdown_dict = {}
        for breakdown in cost_breakdown:
            parts = breakdown.split('|')
            for part in parts:
                key, value = part.strip().split('£')
                key = key.strip()
                value = float(value.strip())
                if key not in breakdown_dict:
                    breakdown_dict[key] = []
                breakdown_dict[key].append(value)
        return breakdown_dict

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
        return []

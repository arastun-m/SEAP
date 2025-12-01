"""Streamlit Chatbot Application."""

import os
from typing import Annotated
import asyncio
import nest_asyncio
import json

import streamlit as st
from openai import AzureOpenAI
from semantic_kernel.kernel import Kernel
from semantic_kernel.agents import AzureAIAgent, ChatCompletionAgent

from sk_orchestrator import SemanticKernelOrchestrator
from agents.chart_plotter import ChartPlotterPlugin
from agents.admin_info import AdminInfoPlugin
from config import AOAI_ENDPOINT, AOAI_DEPLOYMENT
from sk_open_ai import get_aoai_chat_completion_service
from cosmos_db import CosmosDBClient

#apply nest_asyncio to allow async code to run in streamlit
nest_asyncio.apply()


class OrchestratorWrapper:
    def __init__(self, user_id):
        # connect to the database and validate user login
        self.cosmos_client = CosmosDBClient()
        self.user_data = self.validate_user_login(user_id)
        self.user_id = user_id if self.user_data else None

        # initialise agentic setup
        self.orchestrator = SemanticKernelOrchestrator(self.cosmos_client)
        asyncio.run(self.orchestrator.initialise_orchestrator())
        
    def validate_user_login(self, user_id) -> Annotated[dict, "User data"]:
        """Validates user login based on matching user_id."""
        # mocked: does not check passwords or any real authentication
        user_container = self.cosmos_client.containers_proxy.get("users")
        items = user_container.query_items(
            query="SELECT * FROM c where c.id=@user_id",
            parameters=[{"name": "@user_id", "value": user_id}],
            enable_cross_partition_query=True
        )
        for item in items: # cleanup item by removing metadata fields
            item.pop("_rid", None)
            item.pop("_self", None)
            item.pop("_etag", None)
            item.pop("_attachments", None)
            item.pop("_ts", None)
        return item

    async def generate_response(self, query):
        try:
            # ground with logged-in user_id
            input_message = {
                "user_id": self.user_id,
                "user_role": self.user_data.get("role", "user"),
                "content": query
            }
            return await self.orchestrator.process_message(input_message)
        except Exception as e:
            st.error(f"Error connecting to the orchestrator: {e}")
            return "Sorry, I could not connect to the orchestrator."
    
    def log_out(self):
        """Clears all charts on logout"""
        chart_dir = "charts/"
        if os.path.exists(chart_dir):
            for file in os.listdir(chart_dir):
                file_path = os.path.join(chart_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")

def main():
    # streamlit app setup
    st.title("Conversational Energy Management")
    login_message = "Please log in with your User ID to get started."
    welcoming_message = """
        Welcome back {name}! You can ask anything related to energy management in our campus.
        """

    if st.session_state.get("just_logged_in"):
        name = st.session_state.assistant.user_data.get("first_name", "User")
        st.success(welcoming_message.format(name=name))
        st.session_state.just_logged_in = False  # Reset after showing

    if "user_id" not in st.session_state:
        st.session_state.user_id = ""
    if "assistant" not in st.session_state:
        st.session_state.assistant = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # login
    if not st.session_state.assistant:
        st.subheader(login_message)
        user_id_input = st.text_input("User ID", key="user_id_input")
        if st.button("Login"):
            if user_id_input:
                assistant = OrchestratorWrapper(user_id_input)
                if assistant.user_id: # succesful login
                    st.session_state.user_id = user_id_input
                    st.session_state.assistant = assistant
                    st.session_state.just_logged_in = True
                    st.rerun()
                else:
                    st.error("User ID not found. Please try again.")
            else:
                st.warning("Please enter your User ID.")
        return  # Stop here until login is successful

    # sidebar: Logout and Tools
    with st.sidebar:
        if st.button("🔓 Logout"):
            st.session_state.assistant.log_out()
            st.session_state.assistant = None
            st.session_state.user_id = ""
            st.session_state.messages = []
            st.rerun()

    # chatbot interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            for chart in message.get("chart", []):
                st.image(chart, caption="Generated Chart")

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt,
                                          "user_id": st.session_state.user_id})
        with st.chat_message("user"):
            st.markdown(prompt)

        assistant = st.session_state.assistant
        # response: {"text": str, "error": str, "chart": ["path_to_plot", "path_to_plot2", ...]}
        response = asyncio.run(assistant.generate_response(prompt))
        print(f"final response: {response}")
        #response = llm_agent(prompt)

        with st.chat_message("assistant"):
            if response.get("chart"):
                for chart_path in response["chart"]:
                    print("Displaying chart:", chart_path)
                    st.image(chart_path, caption=f"Generated Chart")
            st.markdown(response["text"])

        st.session_state.messages.append({"role": "assistant", "content": response["text"], "chart": response.get("chart", []),})


# chart tests
if __name__ == "__main__":
    main()
    # # testing ChartPlotterPlugin
    # cosmos_client = CosmosDBClient()
    # chart_plugin = ChartPlotterPlugin(cosmos_client)
    # # #chart_path = chart_plugin.plot_room_status("LT1", "co2")
    # # #chart_path = chart_plugin.plot_zone_status("zone_lecture", "temperature")
    # # #chart_path = chart_plugin.plot_building_status("bldg_eng", "co2")
    # # # chart_path = chart_plugin.plot_zone_metrics("zone_lecture", "cost breakdown")
    # # chart_paths = chart_plugin.plot_building_metrics("bldg_eng", "cost breakdown")
    # chart_paths = chart_plugin.plot_user_feedback()
    # print(f"Chart saved at: {chart_paths}")

    # #print(chart_plugin.get_hvac_action_data("zone_lecture", "usage"))

    # testing AdminInfoPlugin
    #admin_info_plugin = AdminInfoPlugin(cosmos_client)
    #print(admin_info_plugin.get_room_status_data("LT1"))
    #print(admin_info_plugin.get_hvac_action_data("zone_lecture"))
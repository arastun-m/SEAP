""" Azure AI Agent clients, for Azure AI Foundry-based evaluations 

trying to run Azure AI Agent -based evaluations; problems:
1. self.project_client.agents.runs.create_and_process run status failed
Run failed: {'code': 'server_error', 'message': 'Sorry, something went wrong.'}
"""

import json
import os
from azure.ai.projects import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent

# Specalised Agent Plugins
from agents.campus_info import CampusInfoPlugin, get_ai_agent_tools

from sk_open_ai import get_aoai_chat_completion_service
from utils import load_prompt_string
import config


class AIAgentClients:
    def __init__(self):
        self.project_endpoint = config.AGENTS_PROJECT_ENDPOINT
        self.credential = DefaultAzureCredential()
        self.project_client = None
        self.agents = None
        self.agent_ids = None
    
    def load_agent_ids(self) -> dict:
        path = "../../config.json" # hardcoded for evaluation
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Failed loading agent ids, file not found at {config.AGENT_IDS_FILE}")
        return {}

    async def initialise_clients(self):
        async with DefaultAzureCredential(exclude_interactive_browser_credential=False) as creds:
            async with AzureAIAgent.create_client(credential=creds, endpoint=self.project_endpoint) as self.project_client:
                self.project_client.agents.enable_auto_function_calls(tools=get_ai_agent_tools())
                self.agent_ids = self.load_agent_ids()
                self.agents = await self.initialise_agents()

                thread = await self.project_client.agents.threads.create()
                message = await self.project_client.agents.messages.create(
                    thread_id=thread.id,
                    role="user",  # Role of the message sender
                    content="What buildings are available in the campus?",  # Message content
                )
                run = await self.project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=self.agents["CampusInfo"].id)
                print(f"Run finished with status: {run.status}")

                if run.status == "failed":
                    print(f"Run failed: {run.last_error}")

                # # Fetch and log all messages
                # messages = self.project_client.agents.messages.list(thread_id=thread.id)
                # for message in messages:
                #     print(f"Role: {message.role}, Content: {message.content}")
                    


    async def initialise_agents(self) -> list:
        agents = {}
        for agent_name, agent_id in self.agent_ids.items():
            try:
                agent_definition = await self.project_client.agents.get_agent(agent_id)
                agents[agent_name] = agent_definition
                print(f"Initialised agent: {agent_name} with ID: {agent_id}")
            except Exception as e:
                print(f"Failed to initialise agent {agent_name} with ID {agent_id}: {e}")
        return agents

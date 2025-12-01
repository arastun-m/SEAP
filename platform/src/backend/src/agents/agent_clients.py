""" Semantic Kernel-based agent clients, used for modular local evaluation and testing"""

import asyncio
from typing import Dict, List, Any, Optional, Awaitable, Callable

# Semantic Kernel imports
from semantic_kernel import Kernel
from semantic_kernel.agents import (
    ChatCompletionAgent,
    ChatHistoryAgentThread,
)
from semantic_kernel.filters import FunctionInvocationContext

# Specalised Agent Plugins
from agents.campus_info import CampusInfoPlugin
from agents.user_feedback import UserFeedbackPlugin
from agents.admin_info import AdminInfoPlugin
from agents.chart_plotter import ChartPlotterPlugin

from cosmos_db import CosmosDBClient
from sk_open_ai import get_aoai_chat_completion_service
from utils import load_prompt_string
import config


class AgentClients:
    def __init__(self, model_deployment: str = "gpt-4o", alternative_instructions=None):
        """ Defines and initialises the agent clients """

        # agent metadata definition
        self.model_deployment = model_deployment
        self.cosmos_client = CosmosDBClient()
        self.agent_names = config.AGENT_NAMES
        self.agent_intructions_paths = [config.PROMPT_CAMPUS_INFO, config.PROMPT_FEEDBACK_COLLECTOR,
                                        config.PROMPT_ADMIN_INFO, config.PROMPT_CHART_PLOTTER]
        self.plugin_groups = [[CampusInfoPlugin(self.cosmos_client)],
                              [UserFeedbackPlugin(self.cosmos_client)],
                              [AdminInfoPlugin(self.cosmos_client)],
                              [ChartPlotterPlugin(self.cosmos_client)]]
        
        self.agent_metadata = {} # {name: "agent_name", instructions: "instructions", plugin: "plugin_instance"}
        for i in range(len(self.agent_names)):
            self.agent_metadata[self.agent_names[i]] = {
                "name": self.agent_names[i],
                "instructions": load_prompt_string(self.agent_intructions_paths[i]) if not alternative_instructions else load_prompt_string(alternative_instructions),
                "plugins": self.plugin_groups[i] if self.plugin_groups[i] else None
            }

        self.kernel = Kernel()
        self.kernel.add_filter("function_invocation", self.function_invocation_filter)
        self.clients: Dict[str, ChatCompletionAgent] = {}
        self.initialize_clients() # initialize all agents
        # tool calling and storage
        self.tool_calls = []
        self.tool_definitions= []
    
    def initialize_clients(self):
        for agent_name in self.agent_names: self.add_client(agent_name)

    def add_client(self, agent_name) -> None:
        agent = ChatCompletionAgent(
            service=get_aoai_chat_completion_service(self.model_deployment),
            kernel=self.kernel,
            name=agent_name,
            instructions=self.agent_metadata[agent_name]["instructions"],
            plugins=self.agent_metadata[agent_name]["plugins"],
        )
        self.clients[agent_name] = agent

    async def get_response(self, agent_name: str, query: str, thread: ChatHistoryAgentThread = None) -> dict:
        """ get a result including agent response, tool definitions and tool calls """
        if agent_name not in self.clients:
            print(f"Agent {agent_name} not found.")
            return None
        agent = self.clients[agent_name]

        self.tools_calls = [] # reset
        self.tool_definitions = []
        agent_plugin = self.agent_metadata[agent_name]["plugins"] if self.agent_metadata[agent_name]["plugins"] else None
        if agent_plugin:
            for plugin in agent_plugin:
                self.tool_definitions.extend(plugin.get_all_tools_definitions())
        else: self.tool_definitions = []

        response = await agent.get_response(messages=query, thread=thread)
        return {"response": response.message.__str__(), "tool_calls": self.tool_calls, "tool_definitions": self.tool_definitions}
    
    async def function_invocation_filter(self, context: FunctionInvocationContext, next: Callable[[FunctionInvocationContext], Awaitable[None]]) -> None:
        """ Captures and stores tool calls made by the agent """
        await next(context)
        arguments = context.arguments # remove 'messages' argument
        if "message" in arguments: del arguments["message"]
        
        self.tool_calls.append({
            "type": "tool_call",
            "tool_call_id": f"call_{context.function.name}",
            "name": context.function.name,
            "arguments": context.arguments
        })

    # ----------------- Chat Loop -----------------
    async def chat(self, agent: ChatCompletionAgent, thread: ChatHistoryAgentThread = None) -> bool:
        """
        Continuously prompt the user for input and show the assistant's response.
        Type 'exit' to exit.
        """
        mock_id = "user_001" # mock
        try:
            user_input = input("User:> ")
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting chat...")
            return False

        if user_input.lower().strip() == "exit":
            print("\n\nExiting chat...")
            return False

        message = "User ID: " + mock_id + "\n" + user_input
        response = await agent.get_response(
            messages=message,
            thread=thread,
        )
        print(f"{agent.name}:> {response.message.__str__()}")
        return True
"""Semantic Kernel Orchestrator

1. Orchestrator | Initialisation, Message Processing 
"""

import json
from json import JSONDecodeError
from typing import Annotated

from azure.identity.aio import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.ai.projects import AIProjectClient
from semantic_kernel.agents import AzureAIAgent, ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel import Kernel

# Specalised Agent Plugins
from agents.campus_info import CampusInfoPlugin
from agents.user_feedback import UserFeedbackPlugin
from agents.admin_info import AdminInfoPlugin
from agents.chart_plotter import ChartPlotterPlugin

# Clients and Utilities
from sk_open_ai import AOAIClient, AOAIRAGClient, get_aoai_chat_completion_service
from clu_client import CLUClient
from cqa_client import CQAClient
from cosmos_db import CosmosDBClient
from utils import load_prompt_string
import config


class SemanticKernelOrchestrator:
    """
    Orchestrator for managing agent interactions and message processing.
    """

    def __init__(self, cosmos_client: CosmosDBClient, model_deployment: str = "gpt-4o"):
        self.project_endpoint = config.AGENTS_PROJECT_ENDPOINT
        self.aoai_endpoint = config.AOAI_ENDPOINT
        self.aoai_deployment = model_deployment # default model deployment
        self.search_endpoint = config.SEARCH_ENDPOINT
        self.search_key = config.SEARCH_KEY
        self.search_index_name = config.SEARCH_INDEX_BLOB_NAME # using blob index for RAG

        self.extract_instructions_path = config.PROMPT_EXTRACT_UTTERANCES
        self.agent_names = config.AGENT_NAMES
        self.max_retries = 3

        # defining components
        self.kernel = Kernel()
        self.thread: ChatHistoryAgentThread = ChatHistoryAgentThread()
        self.cosmos_client = cosmos_client
        self.extract_client = None
        self.clu_client = None
        self.cqa_client = None
        self.rag_client = None
        self.agent_ids = None
        self.project_client = None
        self.agents = {}
        self.agent_group_chat = None

        # specialised agents
        self.agent_plugins = {}
        self.plugins = [[CampusInfoPlugin(self.cosmos_client)],
                        [UserFeedbackPlugin(self.cosmos_client)],
                        [AdminInfoPlugin(self.cosmos_client)],
                        [ChartPlotterPlugin(self.cosmos_client)]]
        for i in range(len(self.agent_names)): 
            self.agent_plugins[self.agent_names[i]] = self.plugins[i]

    async def initialise_orchestrator(self):
        print("Initialising Semantic Kernel Orchestrator...")
        extraction_instructions = load_prompt_string(self.extract_instructions_path)
        self.extract_client = AOAIClient(self.aoai_endpoint, self.aoai_deployment, instructions=extraction_instructions)
        print("Extract client initialised.")
        self.clu_client = CLUClient()
        print("CLU client initialised.")
        self.cqa_client = CQAClient()
        print("CQA client initialised.")
        self.rag_client = AOAIRAGClient(self.aoai_endpoint, self.aoai_deployment, self.search_endpoint,
                                         self.search_key, self.search_index_name)
        print("RAG client initialised.\n")

        try:
            async with DefaultAzureCredential(exclude_interactive_browser_credential=False) as creds:
                async with AzureAIAgent.create_client(credential=creds, endpoint=self.project_endpoint) as self.project_client:
                    self.agent_ids = self.load_agent_ids()
                    self.agents = await self.initialise_agents()
                    print("Project client initialised.\n")
                    
        except Exception as e:
            print(f"Error during setup: {e}")
    
    def load_agent_ids(self) -> Annotated[dict, "Agent IDs"]:
        try:
            with open(config.AGENT_IDS_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Failed loading agent ids, file not found at {config.AGENT_IDS_FILE}")
        return {}
    
    async def initialise_agents(self) -> list:
        agents = {}
        for agent_name, agent_id in self.agent_ids.items():
            try:
                agent_definition = await self.project_client.agents.get_agent(agent_id)
                agent = ChatCompletionAgent(
                    service=get_aoai_chat_completion_service(),
                    kernel=self.kernel,
                    name=agent_definition["name"],
                    instructions=agent_definition["instructions"],
                    plugins=self.agent_plugins.get(agent_name, None),
                )
                agents[agent_name] = agent
                print(f"Initialised agent: {agent_name} with ID: {agent_id}")
            except Exception as e:
                print(f"Failed to initialise agent {agent_name} with ID {agent_id}: {e}")

        agents["Triage"] = ChatCompletionAgent(
            service=get_aoai_chat_completion_service(),
            kernel=self.kernel,
            name="Triage",
            instructions=load_prompt_string(config.PROMPT_TRIAGE),
            plugins=[agents["CampusInfo"], agents["Feedback"], agents["AdminInfo"], agents["ChartPlotter"]],
        )
        return agents

    async def process_message(self, input_message: str):
        """ Response Format {text: str, error: str, chart: [fig]}"""
        response = {"text": "", "error": "", "chart": []}
        retry_count = 0
        last_exception = None

        while retry_count < self.max_retries:
            try:
                # ORCHESTRATION PIPELINE
                # 1. initial CQA check
                cqa_result = self.cqa_client.get_cqa_result(input_message["content"])
                cqa_answer = cqa_result.get("answers")[0].get("answer")
                if cqa_answer != "No good match found in KB": 
                    print("CQA found a relevant answer.")
                    response["text"] = cqa_answer
                    return response

                # 2. CLU routing => {[Specialised Agents], RAG fallback}
                clu_result = self.clu_client.get_clu_result(input_message["content"])
                if clu_result.get("error"):
                    print(f"Error in CLU processing: {clu_result['error']}")
                    continue
                intent = clu_result.get("result").get("prediction").get("topIntent")
                intend_confidence = clu_result.get("result").get("prediction").get("intents", {})[0].get("confidenceScore", 0.0)
                input_message["intent"] = intent
                input_message["confidence"] = intend_confidence

                # 3. RAG if no intend matched
                if intent == "None":
                    print("No intent matched, falling back to RAG.")
                    rag_result = await self.rag_client.chat_completion(input_message)
                    if rag_result and isinstance(rag_result, str):
                        response["text"] = rag_result
                        return response
                    
                # Ablation: No Triage
                # if intent == "Info":
                #     if input_message["user_role"].lower() == "admin":
                #         intent = "AdminInfo"
                #     else:
                #         intent = "CampusInfo"
                # elif intent == "Analysis":
                #     intent = "AdminInfo"
                # elif intent == "Feedback":
                #     intent = "Feedback"
                # elif intent == "Chart":
                #     intent = "ChartPlotter"
                # agent_result = await self.agents[intent].get_response(messages=message_to_str(input_message), thread=self.thread)

                # 4. Triage Agent
                agent_result = await self.agents["Triage"].get_response(messages=message_to_str(input_message), thread=self.thread)

                # Final response processing
                try:
                    json_res = json.loads(str(agent_result.content))  # Check if the result is valid JSON
                    response["text"] = json_res.get("text", agent_result.content)
                    response["chart"] = json_res.get("chart", [])
                    return response
                except JSONDecodeError:
                    response["text"] = agent_result.content.content
                    response["error"] = "Invalid JSON response from agent, returning as is."
                    return response
        
            except Exception as e:
                last_exception = e
                retry_count += 1
                print(f"Error processing message, retrying {retry_count}/{self.max_retries}: {e}")
                continue

        print("Max retries reached, returning last exception.")
        if last_exception:
            return {"error": last_exception}


def message_to_str(message: dict) -> str:
    """Converts structured user query message dict to string to be passed into the agent.
    
    message: {
        "user_id": str,
        "user_role": str,
        "content": str,
        "intent": str,
        "confidence": float
    }
    """
    return f"METADATA: user ID: {message['user_id']} with role {message['user_role']}, intend: {message['intent']} with confidence {message['confidence']}\nMESSAGE: {message['content']}"
""" Evaluating specialised agents.

1. Agent-Specific:
- Intent Resolution (query, response)
- Tool Call Accuracy (query, tool_calls, tool_definitions)
- Task Adherence (query, response)
2. General Purpose:
- Relevance (query, response)
- Coherence (query, response)
- Fluency (response)
3. Response Level Metrics:
- Latency (time taken to get response)
- Answer Length (number of tokens in response)
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from pprint import pprint

from azure.ai.evaluation import (
    evaluate, AzureOpenAIModelConfiguration,
    IntentResolutionEvaluator, ToolCallAccuracyEvaluator, TaskAdherenceEvaluator, # agentic evaluators
    CoherenceEvaluator, FluencyEvaluator, RelevanceEvaluator # general purpose evaluators
)
from semantic_kernel.agents import ChatHistoryAgentThread

from eval_config import (
    SYNTHETIC_DATA_PATHS, GROUND_TRUTH_PATHS, DATASET_PATHS, RESULT_PATHS,
    AOAI_ENDPOINT, AgentClients,
)
from eval_config import (
    GPT4_AOAI_KEY, GPT4_DEPLOYMENT, GPT4_MINI_AOAI_KEY, GPT4_MINI_DEPLOYMENT, 
    PHI4_AOAI_KEY, PHI4_DEPLOYMENT, LLAMA3_INSTRUCT_AOAI_KEY, LLAMA3_INSTRUCT_DEPLOYMENT,
    PHI4_MINI_INSTRUCT_AOAI_KEY, PHI4_MINI_INSTRUCT_DEPLOYMENT
)
from eval_utils import EvalDataHandling


class AgentEval:
    """ Agent Evaluation Class
    
    1. Generates an evaluation dataset based on ground truth
    2. Evaluates the dataset using agentic and general purpose evaluators
    """

    def __init__(self, agent_name: str = "CampusInfo", eval_run_name: str = "gpt-4o",
                 model_deployment: str = "gpt-4o", alternative_instructions=None):
        self.agent_name = agent_name
        self.eval_data_handler = EvalDataHandling()   
        self.ground_truth_path = GROUND_TRUTH_PATHS[self.agent_name.lower()]
        self.dataset_path = DATASET_PATHS[self.agent_name.lower()]
        self.results_path = RESULT_PATHS[self.agent_name.lower() + "_all"][eval_run_name]

        self.agent_clients = AgentClients(model_deployment=model_deployment, alternative_instructions=alternative_instructions) # initialise agent clients
        self.judge_config = AzureOpenAIModelConfiguration( # LLM-judge config
            azure_endpoint=AOAI_ENDPOINT,
            api_key=GPT4_AOAI_KEY,
            azure_deployment=GPT4_DEPLOYMENT,
            api_version="2024-12-01-preview",
        )
        self.synthetic_text = self.eval_data_handler.get_synthetic_data(SYNTHETIC_DATA_PATHS["manual"])

    def generate_benchmark(self) -> None:
        """ Generates the evaluation dataset based on given queries and ground truth """
        ground_truth_data = self.eval_data_handler.get_eval_dataset(self.ground_truth_path)
        eval_data = []
        thread: ChatHistoryAgentThread = ChatHistoryAgentThread()
        mock_id = "user_001"  # Mock user ID for testing

        for line in ground_truth_data:
            line["query"] = f"User ID: {mock_id}\n{line['query']}"  # Add mock user ID to each query
            start_time = time.time()
            result = asyncio.run(
                self.agent_clients.get_response(agent_name=self.agent_name, query=line["query"], thread=thread)
            )
            end_time = time.time()

            eval_data.append({
                "query": line["query"],
                "context": "", # no context from Agents
                "tools_definitions": result["tool_definitions"],
                "tools_calls": result["tool_calls"],
                "response": result,
                "ground_truth": line["ground_truth"],
                "answer_length": len(result["response"]),
                "latency": end_time - start_time
            })
        self.eval_data_handler.write_eval_dataset(eval_data, self.dataset_path)
        print(f"Generated benchmark data with {len(eval_data)} entries, saved to {self.dataset_path}")

    def evaluate(self) -> None:
        """ Given the evaluation dataset, runs Agent evaluations and stores results. """
        evaluate(
            data=self.dataset_path,
            evaluators={
                "intend_resolution": IntentResolutionEvaluator(model_config=self.judge_config, threshold=3),
                "tool_call_accuracy": ToolCallAccuracyEvaluator(model_config=self.judge_config, threshold=3),
                "task_adherence": TaskAdherenceEvaluator(model_config=self.judge_config, threshold=3),
                "relevance": RelevanceEvaluator(model_config=self.judge_config, threshold=3),
                "coherence": CoherenceEvaluator(model_config=self.judge_config, threshold=3),
                "fluency": FluencyEvaluator(model_config=self.judge_config, threshold=3),
            },
            evaluator_config={
                "default": {
                    "column_mapping": {
                        "query": "${data.query}",
                        "context": "${data.context}",
                        "tool_definitions": "${data.tools_definitions}",
                        "tool_calls": "${data.tools_calls}",
                        "response": "${data.response}",
                        "ground_truth": "${data.ground_truth}",
                    } 
                }
            },
            output_path=self.results_path,
        )
        print(f"Evaluation completed. Results saved to {self.results_path}")



# ================================= EVALUATION TYPES (LLMs, ReAct Ablation, Query Types) ============================
def run_model_evaluations(agent_name: str = "CampusInfo"):
    """ Runs evaluations with different LLM models """
    model_deployments = [GPT4_DEPLOYMENT, GPT4_MINI_DEPLOYMENT, LLAMA3_INSTRUCT_DEPLOYMENT, PHI4_MINI_INSTRUCT_DEPLOYMENT]
    models = ["gpt4o", "gpt4o_mini", "llama3-instruct", "phi4_mini_instruct"]

    model_deployments = [GPT4_MINI_DEPLOYMENT]
    models = ["gpt4o_mini"]

    for model, model_deployment in zip(models, model_deployments):
        print(f"Running evaluations for model: {model}")
        agent_eval = AgentEval(agent_name=agent_name, eval_run_name=model, model_deployment=model_deployment)
        agent_eval.generate_benchmark()
        agent_eval.evaluate()
        print(f"Evaluations for model {model} completed.\n")
    
def run_few_shot_prompting_evaluations(agent_name: str = "CampusInfo"):
    """ Runs evaluations with different few-shot prompting techniques """
    few_shot_methods = ["no_examples", "simple_examples", "react_examples"]
    alternative_inst_path_start = "../../../evals/prompt_variations/" + agent_name.lower() + "_" 
    alternative_instruction_paths = [
        alternative_inst_path_start + "none.txt",
        alternative_inst_path_start + "simple.txt",
        alternative_inst_path_start + "react.txt"
    ]

    for few_shot_method, alternative_instruction in zip(few_shot_methods, alternative_instruction_paths):
        print(f"Running evaluations for few-shot method: {few_shot_method}")
        agent_eval = AgentEval(agent_name=agent_name, eval_run_name=few_shot_method,
                               model_deployment=GPT4_DEPLOYMENT, alternative_instructions=alternative_instruction)
        agent_eval.generate_benchmark()
        agent_eval.evaluate()
        print(f"Evaluations for few-shot method {few_shot_method} completed.\n")

def run_query_type_evaluations(agent_name: str = "CampusInfo"):
    """ Run evaluation with different evaluation query types: single-utterance vs multi-utterance"""
    query_types = ["single_utterance_queries", "multi_utterance_queries"]
    query_ground_truth_paths = [GROUND_TRUTH_PATHS[agent_name.lower()], GROUND_TRUTH_PATHS[agent_name.lower() + "_multi"]]

    # 1. single-utterance queries
    agent_eval = AgentEval(agent_name=agent_name, eval_run_name=query_types[0])
    agent_eval.ground_truth_path = query_ground_truth_paths[0]
    agent_eval.generate_benchmark()
    agent_eval.evaluate()
    print(f"Evaluations for single-utterance queries completed.\n")
    # 2. multi-utterance queries
    agent_eval = AgentEval(agent_name=agent_name, eval_run_name=query_types[1])
    agent_eval.ground_truth_path = query_ground_truth_paths[1]
    agent_eval.generate_benchmark()
    agent_eval.evaluate()
    print(f"Evaluations for multi-utterance queries completed.\n")


# Agent evaluatin pipeline
if __name__ == "__main__":
    agent_names = ["AdminInfo"]
    for agent_name in agent_names:
        print(f"Starting evaluations for agent: {agent_name}\n")
        run_model_evaluations(agent_name=agent_name)
        #run_few_shot_prompting_evaluations(agent_name=agent_name)
        #run_query_type_evaluations(agent_name=agent_name)



# if __name__ == "__main__":
#     agent_name = "AdminInfo"
#     agent_client = AgentClients()
#     thread: ChatHistoryAgentThread = ChatHistoryAgentThread()

#     # mock_id = "user_001"
#     # query = "The lighting in Lecture Theatre 1 is very dim during late afternoons."
#     # query = "User ID: " + mock_id + "\n" + query
#     # result = asyncio.run(
#     #     agent_client.get_response(agent_name=agent_name, query=query, thread=thread)
#     # )
#     # print(result["response"])
#     # print(result["tool_calls"])

#     print("Welcome to the chat bot!\n  Type 'exit' to exit.\n")
#     chatting = True
#     while chatting:
#         chatting = asyncio.run(agent_client.chat(agent_client.clients[agent_name], thread=thread))

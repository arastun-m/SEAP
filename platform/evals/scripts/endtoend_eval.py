"""
Evaluating the End-to-End Conversational System
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from pprint import pprint

from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import (
    evaluate, AzureOpenAIModelConfiguration,
    IntentResolutionEvaluator, ToolCallAccuracyEvaluator, TaskAdherenceEvaluator, # agentic evaluators
    CoherenceEvaluator, FluencyEvaluator, RelevanceEvaluator # general purpose evaluators
)
from azure.ai.evaluation.red_team import RedTeam, RiskCategory
from azure.ai.evaluation.red_team import AttackStrategy

from eval_config import (
    SYNTHETIC_DATA_PATHS, GROUND_TRUTH_PATHS, DATASET_PATHS, RESULT_PATHS,
    AOAI_ENDPOINT, SemanticKernelOrchestrator, CosmosDBClient
)
from eval_config import (
    GPT4_AOAI_KEY, GPT4_DEPLOYMENT, GPT4_MINI_AOAI_KEY, GPT4_MINI_DEPLOYMENT, 
    PHI4_AOAI_KEY, PHI4_DEPLOYMENT, LLAMA3_INSTRUCT_AOAI_KEY, LLAMA3_INSTRUCT_DEPLOYMENT,
    PHI4_MINI_INSTRUCT_AOAI_KEY, PHI4_MINI_INSTRUCT_DEPLOYMENT,
    AGENTS_PROJECT_ENDPOINT
)
from eval_utils import EvalDataHandling


class EndToEndEval():
    """ End-to-End RAG Evaluation Class
    """
    def __init__(self, eval_run_name: str = "gpt-4o", model_deployment: str = "gpt-4o"):
        self.agent_name = "EndToEnd"
        self.eval_data_handler = EvalDataHandling()
        self.ground_truth_path = GROUND_TRUTH_PATHS[self.agent_name.lower()]
        self.dataset_path = DATASET_PATHS[self.agent_name.lower()]
        self.results_path = RESULT_PATHS[self.agent_name.lower() + "_all"][eval_run_name]
        
        self.cosmos_client = CosmosDBClient()
        self.orchestrator = SemanticKernelOrchestrator(self.cosmos_client, model_deployment=model_deployment)
        asyncio.run(self.orchestrator.initialise_orchestrator())
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
        for line in ground_truth_data:
            # User query + ground truth
            input_message = {
                "user_id": line["user_id"],
                "user_role": line["user_role"],
                "content": line["query"]
            }
            line["query"] = str(input_message)
            start_time = time.time()
            result = asyncio.run( # response = {"text": "", "error": "", "chart": []}
                self.orchestrator.process_message(input_message)
            )
            
            end_time = time.time()

            eval_data.append({
                "query": line["query"],
                "context": "", # no context from Agents
                "response": str(result),
                "ground_truth": line["ground_truth"],
                "answer_length": len(str(result)),
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
                        "response": "${data.response}",
                        "ground_truth": "${data.ground_truth}",
                    } 
                }
            },
            output_path=self.results_path,
        )
        print(f"Evaluation completed. Results saved to {self.results_path}")
    
    def evaluate_redteam(self) -> None:
        """ Evaluates risk and safety using AI Red Teaming framework """
        azure_ai_project = AGENTS_PROJECT_ENDPOINT
        red_team_agent = RedTeam(
            azure_ai_project=azure_ai_project, # required
            credential=DefaultAzureCredential() # required
        )

        def callback(query: str) -> str:
            """ Callback to the end-to-end system.
            Reformats all str query into the expected dict input format.
            """
            input_message = {
                "user_id": "user_014", # mock user ID
                "user_role": "Admin", # mock user role
                "content": query
            }
            return str(asyncio.run(self.orchestrator.process_message(input_message)))

        # baseline direct adversarial queiries
        asyncio.run(red_team_agent.scan(
            target=callback,
            scan_name="End-to-End System Safety Scan",
            risk_categories=[ # optional, defaults to all four risk categories
                RiskCategory.Violence,
                RiskCategory.HateUnfairness,
                RiskCategory.Sexual,
                RiskCategory.SelfHarm
            ],
            attack_strategies=[ # optional, defaults to all three attack strategies
                AttackStrategy.EASY, 
                AttackStrategy.MODERATE,  
                AttackStrategy.DIFFICULT,
            ],
            output_path=self.results_path,
        ))

# ================================= EVALUATION TYPES (LLMs, Routing Ablations, Query Types, Safety) ============================
def run_model_evaluations():
    """ Runs evaluations with different LLM models """
    model_deployments = [GPT4_DEPLOYMENT, GPT4_MINI_DEPLOYMENT, LLAMA3_INSTRUCT_DEPLOYMENT, PHI4_MINI_INSTRUCT_DEPLOYMENT]
    models = ["gpt4o", "gpt4o_mini", "llama3-instruct", "phi4_mini_instruct"]

    for model, model_deployment in zip(models, model_deployments):
        print(f"Running evaluations for model: {model}")
        endtoend_eval = EndToEndEval(eval_run_name=model, model_deployment=model_deployment)
        endtoend_eval.generate_benchmark()
        endtoend_eval.evaluate()
        print(f"Evaluations for model {model} completed.\n")

def run_routing_ablation_evaluations():
    """ Runs evaluations with different routing ablations 

    Note: for simplicity ablation not automated but manually changed before each run.
    1. no_clu: routes queries directly to Triage without CLU intend assistance
    2. no_triage: removes Triage agent, relies entirely on CLU routing to specialised agents
    3. no_cqa: removes CQA step, (CQA either answered by RAG or specialised agents)
    4. no_rag: removes RAG step, intend: None is also routed to Triage

    For automated ablations we would need a new instance of the orchestrator with the relevant step removed for each ablation.
    """
    ablation_types = ["no_clu", "no_triage", "no_cqa", "no_rag"]

    # Ablation step
    ablation_step = 0
    print(f"Running evaluations for routing ablation: {ablation_types[ablation_step]}")
    endtoend_eval = EndToEndEval(eval_run_name=ablation_types[ablation_step])
    endtoend_eval.generate_benchmark()
    endtoend_eval.evaluate()
    print(f"Evaluations for routing ablation {ablation_types[ablation_step]} completed.\n")

def run_query_types_evaluations():
    """ Runs evaluations with different query types """
    query_types = ["single_utterance_queries", "multi_utterance_queries"]
    query_ground_truth_paths = [GROUND_TRUTH_PATHS["endtoend"], GROUND_TRUTH_PATHS["endtoend_multi"]]

    # 1. single-utterance queries
    agent_eval = EndToEndEval( eval_run_name=query_types[0])
    agent_eval.ground_truth_path = query_ground_truth_paths[0]
    agent_eval.generate_benchmark()
    agent_eval.evaluate()
    print(f"Evaluations for single-utterance queries completed.\n")
    # 2. multi-utterance queries
    agent_eval = EndToEndEval(eval_run_name=query_types[1])
    agent_eval.ground_truth_path = query_ground_truth_paths[1]
    agent_eval.generate_benchmark()
    agent_eval.evaluate()
    print(f"Evaluations for multi-utterance queries completed.\n")

def run_safety_evaluations():
    """ Runs safety evaluations """
    print(f"Running safety evaluations")
    endtoend_eval = EndToEndEval(eval_run_name="redteam")
    #endtoend_eval.generate_benchmark()
    endtoend_eval.evaluate_redteam()
    print(f"Safety evaluations completed.\n")


if __name__ == "__main__":
    run_model_evaluations()
    #run_routing_ablation_evaluations()
    #run_query_types_evaluations()
    #run_safety_evaluations()
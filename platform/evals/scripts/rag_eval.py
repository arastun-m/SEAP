""" Evaluating fallback RAG """

import asyncio
import time
from typing import Dict, List, Any, Optional, Literal

from azure.ai.evaluation.simulator import Simulator
from azure.ai.evaluation import (
    evaluate, AzureOpenAIModelConfiguration,
    RetrievalEvaluator, GroundednessEvaluator, RelevanceEvaluator
)

from eval_config import (
    SYNTHETIC_DATA_PATHS, DATASET_PATHS, RESULT_PATHS,
    AOAI_ENDPOINT, AOAI_KEY, AOAI_DEPLOYMENT, AOAIRAGClient,
    SEARCH_ENDPOINT, SEARCH_KEY, SEARCH_INDEX_BLOB_NAME
)
from eval_config import (
    GPT4_AOAI_KEY, GPT4_DEPLOYMENT, GPT4_MINI_AOAI_KEY, GPT4_MINI_DEPLOYMENT, 
    PHI4_AOAI_KEY, PHI4_DEPLOYMENT, LLAMA3_INSTRUCT_AOAI_KEY, LLAMA3_INSTRUCT_DEPLOYMENT,
    PHI4_MINI_INSTRUCT_AOAI_KEY, PHI4_MINI_INSTRUCT_DEPLOYMENT
)
from eval_utils import ExactMatchEvaluator, EvalDataHandling


class RAGEval:
    """ RAG Evaluation Class

    1. Generates synthetic evaluation queries
    2. Generates an evaluation dataset using RAG client
    3. Evaluates the dataset; (1) retrieval, (2) grounding, and (3) relevance
    """

    def __init__(self, rag_client: AOAIRAGClient, eval_run_name= "gpt4o"):
        self.rag_client = rag_client
        self.eval_data_handler = EvalDataHandling()    
        self.dataset_path = DATASET_PATHS["rag"]
        self.results_path = RESULT_PATHS["rag_all"][eval_run_name]
    
        # using GPT-4o as the judge model
        self.judge_config = AzureOpenAIModelConfiguration( # LLM-judge config
            azure_endpoint=AOAI_ENDPOINT,
            api_key=GPT4_AOAI_KEY,
            azure_deployment=GPT4_DEPLOYMENT,
            api_version="2024-12-01-preview",
        )
        self.synthetic_text = self.eval_data_handler.get_synthetic_data(SYNTHETIC_DATA_PATHS["manual"])

    def generate_dataset(self) -> None:
        """ Generates an evaluation dataset using simulated RAG query/response pairs. 
        - Runs the simulator to generate query/response pairs (feed the simulator with synthetic system data)
        - Converts the simulated results into evaluation dataset format (JSONL)
        - Adds response level metric results: latency and answer length.
        """
        latencies = []
        async def callback( # define the callback function for the simulator
            messages: Dict[str, List[Dict]],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
        ) -> dict:
            messages_list = messages["messages"]
            latest_message = messages_list[-1] # last message
            query = latest_message["content"]
            start_time = time.time()
            response, context = await self.rag_client.chat_completion_w_context(query) # call RAG client
            end_time = time.time()
            latencies.append(end_time - start_time)

            formatted_response = {
                "content": response,
                "role": "assistant",
                "context": context,
            }
            messages["messages"].append(formatted_response)
            return {"messages": messages["messages"], "stream": stream, "session_state": session_state, "context": context}

        simulator = Simulator(model_config=self.judge_config)
        outputs = asyncio.run(simulator(
            target=callback,
            text=self.synthetic_text,
            max_conersation_turns=1,
            num_queries=2,
        ))
        # convert the output and write to the evaluation dataset
        self.eval_data_handler.to_eval_qr_json_lines(outputs, latencies, self.dataset_path)

    def evaluate(self) -> None:
        """ Given the evaluation dataset, runs RAG evaluations and stores results. """
        evaluate(
            data=self.dataset_path,
            evaluators={
                "retrieval": RetrievalEvaluator(model_config=self.judge_config, threshold=3),
                "grounding": GroundednessEvaluator(model_config=self.judge_config, threshold=3),
                "relevance": RelevanceEvaluator(model_config=self.judge_config, threshold=3),
            },
            evaluator_config={
                "default": {
                    "column_mapping": {
                        "query": "${data.query}",
                        "context": "${data.context}",
                        "response": "${data.response}",
                    } 
                }
            },
            output_path=self.results_path,
        )
        print(f"Evaluation completed. Results saved to {self.results_path}")


# ================================= EVALUATION TYPES (LLMs, Chunk Size, Top N) ============================
def run_model_evaluations():
    # evaluation over different RAG models
    rag_clients = {
        "gpt4o": AOAIRAGClient(
            AOAI_ENDPOINT, GPT4_DEPLOYMENT, SEARCH_ENDPOINT, SEARCH_KEY, SEARCH_INDEX_BLOB_NAME
        ),
        "gpt4o_mini": AOAIRAGClient(
            AOAI_ENDPOINT, GPT4_MINI_DEPLOYMENT, SEARCH_ENDPOINT, SEARCH_KEY, SEARCH_INDEX_BLOB_NAME
        ),
        # "phi4": AOAIRAGClient(
        #     AOAI_ENDPOINT, PHI4_DEPLOYMENT, SEARCH_ENDPOINT, SEARCH_KEY, SEARCH_INDEX_BLOB_NAME
        # ),
        "phi4_mini_instruct": AOAIRAGClient(
            AOAI_ENDPOINT, PHI4_MINI_INSTRUCT_DEPLOYMENT, SEARCH_ENDPOINT, SEARCH_KEY, SEARCH_INDEX_BLOB_NAME
        ),
        "llama3-instruct": AOAIRAGClient(
            AOAI_ENDPOINT, LLAMA3_INSTRUCT_DEPLOYMENT, SEARCH_ENDPOINT, SEARCH_KEY, SEARCH_INDEX_BLOB_NAME
        ),
    }
    for model_name, rag_client in rag_clients.items():
        print(f"Starting RAG evaluation for model: {model_name}")
        rag_eval = RAGEval(rag_client, eval_run_name=model_name)
        rag_eval.generate_dataset()  # Step 1: Generate dataset
        rag_eval.evaluate()  # Step 2: Evaluate the dataset
        print(f"RAG evaluation for model {model_name} completed.\n")

def run_chunk_evaluations():
    # evaluation over different RAG chunk sizes
    chunk_sizes = [300, 1000, 2000]
    for chunk_size in chunk_sizes:
        rag_client = AOAIRAGClient(
            AOAI_ENDPOINT, GPT4_DEPLOYMENT, SEARCH_ENDPOINT, SEARCH_KEY, SEARCH_INDEX_BLOB_NAME,
            chunk_size=chunk_size
        )
        rag_eval = RAGEval(rag_client, eval_run_name=f"chunk_{chunk_size}")
        rag_eval.generate_dataset()  # Step 1: Generate dataset
        rag_eval.evaluate()  # Step 2: Evaluate the dataset
        print(f"RAG evaluation for chunk size {chunk_size} completed.\n")

def run_top_n_evaluations():
    # evaluation over different RAG top-k results
    top_n = [2, 5, 10]
    for n in top_n:
        rag_client = AOAIRAGClient(
            AOAI_ENDPOINT, GPT4_DEPLOYMENT, SEARCH_ENDPOINT, SEARCH_KEY, SEARCH_INDEX_BLOB_NAME,
            top_n=n
        )
        rag_eval = RAGEval(rag_client, eval_run_name=f"top_{n}")
        rag_eval.generate_dataset()  # Step 1: Generate dataset
        rag_eval.evaluate()  # Step 2: Evaluate the dataset
        print(f"RAG evaluation for top-{n} completed.\n")

# RAG Eval Pipeline
if __name__ == "__main__":
    run_top_n_evaluations()
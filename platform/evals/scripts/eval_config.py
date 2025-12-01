""" evaluation configurations and data file paths """

# ================================== FILE PATHS ============================
import os
dir = os.path.dirname(os.path.abspath(__file__)) # directory of current file
SYNTHETIC_DATA_PATHS = {
    "database_meta": os.path.join(dir, "../data/database_meta.md"),
    "manual": os.path.join(dir, "../data/manual.md"),
    "faqs": os.path.join(dir, "../data/faqs.md"),
    "initiatives": os.path.join(dir, "../data/initiatives.md"),
    "protocols": os.path.join(dir, "../data/protocols.md"),
}
GROUND_TRUTH_PATHS = {
    "clu": os.path.join(dir, "../eval_truth/clu_truth.jsonl"),
    "cqa": os.path.join(dir, "../eval_truth/cqa_truth.jsonl"),
    "campusinfo": os.path.join(dir, "../eval_truth/campus_info_truth.jsonl"),
    "campusinfo_multi": os.path.join(dir, "../eval_truth/campus_info_truth_multi.jsonl"),
    "admininfo": os.path.join(dir, "../eval_truth/admin_info_truth.jsonl"),
    "admininfo_multi": os.path.join(dir, "../eval_truth/admin_info_truth_multi.jsonl"),
    "feedback": os.path.join(dir, "../eval_truth/feedback_truth.jsonl"),
    "feedback_multi": os.path.join(dir, "../eval_truth/feedback_truth_multi.jsonl"),
    "chartplotter": os.path.join(dir, "../eval_truth/chart_plotter_truth.jsonl"),
    "chartplotter_multi": os.path.join(dir, "../eval_truth/chart_plotter_truth_multi.jsonl"),
    "endtoend": os.path.join(dir, "../eval_truth/end_to_end_truth.jsonl"),
    "endtoend_multi": os.path.join(dir, "../eval_truth/end_to_end_truth_multi.jsonl"),
}
DATASET_PATHS = {
    "clu": os.path.join(dir, "../eval_dataset/clu_samples.jsonl"),
    "cqa": os.path.join(dir, "../eval_dataset/cqa_samples.jsonl"),
    "rag": os.path.join(dir, "../eval_dataset/rag_samples.jsonl"),
    "campusinfo": os.path.join(dir, "../eval_dataset/campus_info_samples.jsonl"),
    "feedback": os.path.join(dir, "../eval_dataset/feedback_samples.jsonl"),
    "admininfo": os.path.join(dir, "../eval_dataset/admin_info_samples.jsonl"),
    "chartplotter": os.path.join(dir, "../eval_dataset/chart_plotter_samples.jsonl"),
    "endtoend": os.path.join(dir, "../eval_dataset/end_to_end_samples.jsonl"),
}
RESULT_PATHS = {
    "clu": os.path.join(dir, "../eval_results/clu_results.json"),
    "clu_old": os.path.join(dir, "../eval_results/clu_results_old.json"),
    "cqa": os.path.join(dir, "../eval_results/cqa_results.json"),
    "rag_all": {
        "main": os.path.join(dir, "../eval_results/rag_results.json"),
        "gpt4o": os.path.join(dir, "../eval_results/rag_gpt4o_results.json"),
        "llama3-instruct": os.path.join(dir, "../eval_results/rag_llama3_instruct_results.json"),
        "gpt4o_mini": os.path.join(dir, "../eval_results/rag_gpt4o_mini_results.json"),
        "phi4": os.path.join(dir, "../eval_results/rag_phi4_results.json"),
        "phi4_mini_instruct": os.path.join(dir, "../eval_results/rag_phi4_mini_instruct_results.json"),

        "chunk_300": os.path.join(dir, "../eval_results/rag_chunk_300_results.json"),
        "chunk_1000": os.path.join(dir, "../eval_results/rag_chunk_1000_results.json"),
        "chunk_2000": os.path.join(dir, "../eval_results/rag_chunk_2000_results.json"),

        "top_2": os.path.join(dir, "../eval_results/rag_top_2_results.json"),
        "top_5": os.path.join(dir, "../eval_results/rag_top_5_results.json"),
        "top_10": os.path.join(dir, "../eval_results/rag_top_10_results.json"),
    },
    "campusinfo_all": {
        "main": os.path.join(dir, "../eval_results/campus_info_results.json"),
        "gpt4o": os.path.join(dir, "../eval_results/campus_info_gpt4o_results.json"),
        "llama3-instruct": os.path.join(dir, "../eval_results/campus_info_llama3_instruct_results.json"),
        "gpt4o_mini": os.path.join(dir, "../eval_results/campus_info_gpt4o_mini_results.json"),
        "phi4_mini_instruct": os.path.join(dir, "../eval_results/campus_info_phi4_mini_instruct_results.json"),

        "no_examples": os.path.join(dir, "../eval_results/campus_info_no_examples_results.json"),
        "simple_examples": os.path.join(dir, "../eval_results/campus_info_simple_examples_results.json"),
        "react_examples": os.path.join(dir, "../eval_results/campus_info_react_examples_results.json"),

        "single_utterance_queries": os.path.join(dir, "../eval_results/campus_info_single_utterance_queries_results.json"),
        "multi_utterance_queries": os.path.join(dir, "../eval_results/campus_info_multi_utterance_queries_results.json"),
    },
    "admininfo_all": {
        "main": os.path.join(dir, "../eval_results/admin_info_results.json"),
        "gpt4o": os.path.join(dir, "../eval_results/admin_info_gpt4o_results.json"),
        "llama3-instruct": os.path.join(dir, "../eval_results/admin_info_llama3_instruct_results.json"),
        "gpt4o_mini": os.path.join(dir, "../eval_results/admin_info_gpt4o_mini_results.json"),
        "phi4_mini_instruct": os.path.join(dir, "../eval_results/admin_info_phi4_mini_instruct_results.json"),

        "no_examples": os.path.join(dir, "../eval_results/admin_info_no_examples_results.json"),
        "simple_examples": os.path.join(dir, "../eval_results/admin_info_simple_examples_results.json"),
        "react_examples": os.path.join(dir, "../eval_results/admin_info_react_examples_results.json"),

        "single_utterance_queries": os.path.join(dir, "../eval_results/admin_info_single_utterance_queries_results.json"),
        "multi_utterance_queries": os.path.join(dir, "../eval_results/admin_info_multi_utterance_queries_results.json"),
    },
    "feedback_all": {
        "main": os.path.join(dir, "../eval_results/feedback_results.json"),
        "gpt4o": os.path.join(dir, "../eval_results/feedback_gpt4o_results.json"),
        "llama3-instruct": os.path.join(dir, "../eval_results/feedback_llama3_instruct_results.json"),
        "gpt4o_mini": os.path.join(dir, "../eval_results/feedback_gpt4o_mini_results.json"),
        "phi4_mini_instruct": os.path.join(dir, "../eval_results/feedback_phi4_mini_instruct_results.json"),

        "no_examples": os.path.join(dir, "../eval_results/feedback_no_examples_results.json"),
        "simple_examples": os.path.join(dir, "../eval_results/feedback_simple_examples_results.json"),
        "react_examples": os.path.join(dir, "../eval_results/feedback_react_examples_results.json"),

        "single_utterance_queries": os.path.join(dir, "../eval_results/feedback_single_utterance_queries_results.json"),
        "multi_utterance_queries": os.path.join(dir, "../eval_results/feedback_multi_utterance_queries_results.json"),
    },
    "chartplotter_all": {
        "gpt4o": os.path.join(dir, "../eval_results/chart_plotter_gpt4o_results.json"),
        "llama3-instruct": os.path.join(dir, "../eval_results/chart_plotter_llama3_instruct_results.json"),
        "gpt4o_mini": os.path.join(dir, "../eval_results/chart_plotter_gpt4o_mini_results.json"),
        "phi4_mini_instruct": os.path.join(dir, "../eval_results/chart_plotter_phi4_mini_instruct_results.json"),   

        "no_examples": os.path.join(dir, "../eval_results/chart_plotter_no_examples_results.json"),
        "simple_examples": os.path.join(dir, "../eval_results/chart_plotter_simple_examples_results.json"),
        "react_examples": os.path.join(dir, "../eval_results/chart_plotter_react_examples_results.json"),   

        "single_utterance_queries": os.path.join(dir, "../eval_results/chart_plotter_single_utterance_queries_results.json"),
        "multi_utterance_queries": os.path.join(dir, "../eval_results/chart_plotter_multi_utterance_queries_results.json"),
    },
    "endtoend_all": {
        # model-based comparisons
        "gpt4o": os.path.join(dir, "../eval_results/endtoend_gpt4o_results.json"),
        "llama3-instruct": os.path.join(dir, "../eval_results/endtoend_llama3_instruct_results.json"),
        "gpt4o_mini": os.path.join(dir, "../eval_results/endtoend_gpt4o_mini_results.json"),
        "phi4_mini_instruct": os.path.join(dir, "../eval_results/endtoend_phi4_mini_instruct_results.json"),

        # ablations
        "no_clu": os.path.join(dir, "../eval_results/endtoend_no_clu_results.json"),
        "no_triage": os.path.join(dir, "../eval_results/endtoend_no_triage_results.json"),
        "no_cqa": os.path.join(dir, "../eval_results/endtoend_no_cqa_results.json"),
        "no_rag": os.path.join(dir, "../eval_results/endtoend_no_rag_results.json"),

        # different queries
        "single_utterance_queries": os.path.join(dir, "../eval_results/endtoend_single_utterance_queries_results.json"),
        "multi_utterance_queries": os.path.join(dir, "../eval_results/endtoend_multi_utterance_queries_results.json"),

        # red teaming
        "redteam": os.path.join(dir, "../eval_results/redteaming/"),
    }
}
FIG_PATHS = {
    "clu": os.path.join(dir, "../figures/clu"),
    "cqa": os.path.join(dir, "../figures/cqa"),
    "rag": os.path.join(dir, "../figures/rag"),
    "campusinfo": os.path.join(dir, "../figures/campus_info"),
    "feedback": os.path.join(dir, "../figures/feedback"),
    "admininfo": os.path.join(dir, "../figures/admin_info"),
    "chartplotter": os.path.join(dir, "../figures/chart_plotter"),
    "combined_agents": os.path.join(dir, "../figures/combined_agents"),
    "endtoend": os.path.join(dir, "../figures/end_to_end"),
}

# ================================= SYS IMPORTS ============================
import sys
added_path = "../../src/backend/src"
sys.path.append(added_path)

from config import (
    AOAI_ENDPOINT, AOAI_KEY, AOAI_DEPLOYMENT,
    SEARCH_ENDPOINT, SEARCH_KEY, SEARCH_INDEX_BLOB_NAME,
    AGENTS_PROJECT_ENDPOINT,

    # for model-based evaluation
    GPT4_AOAI_KEY, GPT4_DEPLOYMENT,
    GPT4_MINI_AOAI_KEY, GPT4_MINI_DEPLOYMENT,
    LLAMA3_INSTRUCT_AOAI_KEY, LLAMA3_INSTRUCT_DEPLOYMENT,
    PHI4_AOAI_KEY, PHI4_DEPLOYMENT,
    PHI4_MINI_INSTRUCT_AOAI_KEY, PHI4_MINI_INSTRUCT_DEPLOYMENT
)
from clu_client import CLUClient
from cqa_client import CQAClient
from sk_open_ai import AOAIRAGClient, get_aoai_chat_completion_service
from agents.agent_clients import AgentClients
from agents.ai_agent_clients import AIAgentClients
from sk_orchestrator import SemanticKernelOrchestrator
from cosmos_db import CosmosDBClient

if added_path in sys.path:
    sys.path.remove(added_path)

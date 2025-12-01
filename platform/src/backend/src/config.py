import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))
dir = os.path.dirname(os.path.abspath(__file__)) # directory of current file

# Authentication configuration
USE_MI_AUTH = os.getenv("USE_MI_AUTH", "false").lower() == "true"
MI_CLIENT_ID = os.getenv("MI_CLIENT_ID")

# Azure Cosmos DB configuration
AZURE_COSMOSDB_ENDPOINT = os.getenv("AZURE_COSMOSDB_ENDPOINT")
AZURE_COSMOSDB_KEY = os.getenv("AZURE_COSMOSDB_KEY")
AZURE_COSMOSDB_DATABASE_NAME = os.getenv("AZURE_COSMOSDB_DATABASE_NAME", "campus")

# Azure OpenAI configuration
AGENTS_PROJECT_ENDPOINT = os.getenv("AGENTS_PROJECT_ENDPOINT")
AOAI_ENDPOINT = os.getenv("AOAI_ENDPOINT")
AOAI_DEPLOYMENT = os.getenv("AOAI_DEPLOYMENT")
AOAI_KEY = os.getenv("AOAI_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")

# Azure AI Search
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME")
SEARCH_INDEX_BLOB_NAME = os.getenv("SEARCH_INDEX_BLOB_NAME", SEARCH_INDEX_NAME + "-blob")
SEARCH_INDEX_COSMOS_NAME = os.getenv("SEARCH_INDEX_COSMOS_NAME", SEARCH_INDEX_NAME + "-cosmos")

# Azure AI Language
LANGUAGE_ENDPOINT = os.getenv("LANGUAGE_ENDPOINT")
AUTHORING_LANGUAGE_ENDPOINT = os.getenv("AUTHORING_LANGUAGE_ENDPOINT", LANGUAGE_ENDPOINT)
AUTHORING_AOAI_KEY = os.getenv("AUTHORING_AOAI_KEY", AOAI_KEY)

CLU_CONFIDENCE_THRESHOLD = float(os.getenv("CLU_CONFIDENCE_THRESHOLD", 0.5))
CLU_DEPLOYMENT_NAME = os.getenv("CLU_DEPLOYMENT_NAME")
CLU_MODEL_NAME = os.getenv("CLU_MODEL_NAME")
CLU_PROJECT_NAME = os.getenv("CLU_PROJECT_NAME")

CQA_CONFIDENCE_THRESHOLD = float(os.getenv("CQA_CONFIDENCE_THRESHOLD", 0.5))
CQA_DEPLOYMENT_NAME = os.getenv("CQA_DEPLOYMENT_NAME")
CQA_PROJECT_NAME = os.getenv("CQA_PROJECT_NAME")

# System Messages and Prompts
PROMPT_EXTRACT_UTTERANCES = os.path.join(dir, "prompts/extract_utterances.txt")
PROMPT_RAG_GROUNDING = os.path.join(dir, "prompts/rag_grounding.txt")
# Specialised Agent Prompts
PROMPT_TRIAGE = os.path.join(dir, "prompts/triage.txt")
PROMPT_CAMPUS_INFO = os.path.join(dir, "prompts/campus_info.txt")
PROMPT_FEEDBACK_COLLECTOR = os.path.join(dir, "prompts/user_feedback.txt")
PROMPT_ADMIN_INFO = os.path.join(dir, "prompts/admin_info.txt")
PROMPT_CHART_PLOTTER = os.path.join(dir, "prompts/chart_plotter.txt")

# File paths for metadata
AGENT_IDS_FILE = os.path.join(dir, "../../../config.json")
AGENT_NAMES = ["CampusInfo", "Feedback", "AdminInfo", "ChartPlotter"]
MOCK_DATA_DIR = os.path.join(dir, "data/mock_data")
SCHEMA_FILE = os.path.join(dir, "data/schema.yml")

# LLM deployments used for evaluation
GPT4_AOAI_KEY = os.getenv("GPT4_AOAI_KEY")
GPT4_DEPLOYMENT = os.getenv("GPT4_DEPLOYMENT", "gpt-4o")
GPT4_ENDPOINT = os.getenv("GPT4_ENDPOINT")
GPT4_MINI_AOAI_KEY = os.getenv("GPT4_MINI_AOAI_KEY")
GPT4_MINI_DEPLOYMENT = os.getenv("GPT4_MINI_DEPLOYMENT", "gpt-4o-mini")
LLAMA3_INSTRUCT_AOAI_KEY = os.getenv("LLAMA3_INSTRUCT_AOAI_KEY")
LLAMA3_INSTRUCT_DEPLOYMENT = os.getenv("LLAMA3_INSTRUCT_DEPLOYMENT", "Llama-3.3-70B-Instruct")
PHI4_AOAI_KEY = os.getenv("PHI4_AOAI_KEY")
PHI4_DEPLOYMENT = os.getenv("PHI4_DEPLOYMENT", "Phi-4")
PHI4_MINI_INSTRUCT_AOAI_KEY = os.getenv("PHI4_MINI_INSTRUCT_AOAI_KEY")
PHI4_MINI_INSTRUCT_DEPLOYMENT = os.getenv("PHI4_MINI_INSTRUCT_DEPLOYMENT", "Phi-4-mini-instruct")
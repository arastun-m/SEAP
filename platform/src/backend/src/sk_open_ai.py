from openai import AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents.models import VectorizableTextQuery
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from utils import load_prompt_string
import config

token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")


# ----------------- Basic SK Client Definition -----------------
def get_aoai_client():
    return AsyncAzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint=config.GPT4_ENDPOINT,
        azure_ad_token_provider=token_provider,
    )

def get_aoai_chat_completion_service():
    return OpenAIChatCompletion(
        ai_model_id=config.GPT4_DEPLOYMENT,  # This is the deployment name, not model name
        async_client=get_aoai_client(),
    )

def get_aoai_chat_completion_service(model_deployment: str = "gpt-4o"):
    """ Returns the chat completion service with the specified model deployment """
    return OpenAIChatCompletion(
        ai_model_id=model_deployment,
        async_client=get_aoai_client(),
    )

# ----------------- AOAI client | Non-agentic chat completions -----------------
class AOAIClient(AsyncAzureOpenAI):
    """AOAI Client for chat completions"""

    def __init__(
        self, 
        endpoint: str,
        deployment: str,
        instructions: str = None,
        api_version: str = "2024-12-01-preview",
    ):
        AsyncAzureOpenAI.__init__(
            self,
            api_version=api_version,
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
        )
        self.deployment = deployment
        self.instructions = instructions
        self.chat_state = [] # conversation memory
        if self.instructions: self.chat_state.append({"role": "system", "content": self.instructions})

    async def chat_completion(self, message: str) -> str:
        # call chat api
        self.chat_state.append({"role": "user", "content": message})
        response = await self.chat.completions.create(
            model=self.deployment,
            messages=self.chat_state
        )
        response_message = response.choices[0].message
        self.chat_state.append(response_message)
        return response_message.content

class AOAIRAGClient(AOAIClient):
    """AOAI Client with RAG support"""

    def __init__(
        self, 
        endpoint: str,
        deployment: str,
        search_endpoint: str,
        search_key: str,
        index_name: str,
        instructions: str = None,
        top_n: int = 5,
        api_version: str = "2024-12-01-preview",
    ):
        super().__init__(
            endpoint=endpoint,
            deployment=deployment,
            instructions=instructions,
            api_version=api_version,
        )
        self.search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(search_key)
        )
        self.rag_grounding_prompt = load_prompt_string(config.PROMPT_RAG_GROUNDING)
        self.top_n = top_n
    
    def generate_rag_prompt(self, query: str) -> str:
        """
        Generates RAG grounding prompt given query and search client.
        """
        vector_query = VectorizableTextQuery(
            text=query,
            k_nearest_neighbors=50,
            fields="text_vector"
        )
        search_results = self.search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=["title", "chunk"],
            top=self.top_n
        )

        sources_formatted = "=================\n".join(
            [f'TITLE: {doc["title"]}, CONTENT: {doc["chunk"]}' for doc in search_results]
        )
        prompt = self.rag_grounding_prompt.format(
            query=query,
            sources=sources_formatted
        )
        return prompt, sources_formatted

    async def chat_completion(self, message):
        message, _ = self.generate_rag_prompt(message)
        return await super().chat_completion(message)

    async def chat_completion_w_context(self, message: str):
        """ returns response and context """
        message, context = self.generate_rag_prompt(message)
        return await super().chat_completion(message), context


# testing RAG
if __name__ == "__main__":
    import asyncio

    async def main(): 
        rag_client = AOAIRAGClient(
            endpoint=config.AOAI_ENDPOINT,
            deployment=config.AOAI_DEPLOYMENT,
            search_endpoint=config.SEARCH_ENDPOINT,
            search_key=config.SEARCH_KEY,
            index_name=config.SEARCH_INDEX_BLOB_NAME
        )
        response = await rag_client.chat_completion("Tell me about sustainability initiatives in our campus?")
        print(response)

    asyncio.run(main())
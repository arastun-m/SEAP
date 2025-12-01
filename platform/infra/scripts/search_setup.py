import os
from dotenv import load_dotenv
load_dotenv()

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchField, SearchFieldDataType, SearchIndexerIndexProjection, SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters, IndexProjectionMode,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
    AzureOpenAIVectorizer, AzureOpenAIVectorizerParameters,
    SearchIndex, SearchIndexerDataSourceConnection, SearchIndexerDataContainer,
    SearchIndexerSkillset, SplitSkill, AzureOpenAIEmbeddingSkill,
    InputFieldMappingEntry, OutputFieldMappingEntry,
    SearchIndexer, FieldMapping
)


def get_azure_credential():
    use_mi_auth = os.environ.get('USE_MI_AUTH', 'false').lower() == 'true'

    if use_mi_auth:
        mi_client_id = os.environ['MI_CLIENT_ID']
        return ManagedIdentityCredential(
            client_id=mi_client_id
        )

    return DefaultAzureCredential()


class SearchSetup:
    """
    1. Azure Search Index (with vector search)
    2. Azure Search Indexer - Connection to Database (e.g, Azure Blob Storage, Cosmos DB)
    3. Azure Search Indexer - Creates and Adds a Skillset (e.g., to chunk documents and generate embeddings)
    4. Azure Search Indexer - Creates and Indexer (based on the index, data source and skillset)
    """

    def __init__(self):
        # Azure OpenAI
        self.aoai_endpoint = os.environ['AOAI_ENDPOINT']
        self.aoai_key = os.environ.get('AOAI_KEY', None)
        self.embedding_deployment_name = os.environ['EMBEDDING_DEPLOYMENT_NAME']
        self.embedding_model_name = os.environ['EMBEDDING_MODEL_NAME']
        self.embedding_model_dimensions = int(os.environ['EMBEDDING_MODEL_DIMENSIONS'])
        # Azure Search
        self.endpoint = os.environ['SEARCH_ENDPOINT']
        self.search_key = os.environ.get('SEARCH_KEY', None)
        self.credential = AzureKeyCredential(self.search_key) if self.search_key else get_azure_credential()
        self.index_name = os.environ['SEARCH_INDEX_NAME']


class SearchSetupBlob(SearchSetup):
    """
    Sets up Azure AI Search for Azure Blob Storage
    """

    def __init__(self):
        super().__init__()
        # Azure Storage Account
        self.storage_account_name = os.environ['STORAGE_ACCOUNT_NAME']
        self.storage_account_connection_string = os.environ['STORAGE_ACCOUNT_CONNECTION_STRING']
        self.storage_account_key = os.environ['STORAGE_ACCOUNT_KEY']
        self.blob_container_name = os.environ['BLOB_CONTAINER_NAME']
        # Data Source, Skillset and Indexer names
        self.index_name = os.environ['SEARCH_INDEX_BLOB_NAME']
        self.data_source_name = self.index_name + '-ds'
        self.skillset_name = self.index_name + '-ss'
        self.indexer_name = self.index_name + '-idxr'
    
    def create_search_index(self):
        """
        Create or update the Azure Search index with vector search configuration.
        """
        index_client = SearchIndexClient(endpoint=self.endpoint, credential=self.credential)
        fields = [
            SearchField(name="parent_id", type=SearchFieldDataType.String),
            SearchField(name="title", type=SearchFieldDataType.String),
            SearchField(name="chunk_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True, analyzer_name="keyword"),
            SearchField(name="chunk", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),
            SearchField(name="text_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), vector_search_dimensions=self.embedding_model_dimensions, vector_search_profile_name="hnswSearch")
        ]

        # Vector search configuration
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="hnswConfig"),
            ],
            profiles=[
                VectorSearchProfile(
                    name="hnswSearch",
                    algorithm_configuration_name="hnswConfig",
                    vectorizer_name="aoaiVec",
                )
            ],
            vectorizers=[
                AzureOpenAIVectorizer(
                    vectorizer_name="aoaiVec",
                    kind="azureOpenAI",
                    parameters=AzureOpenAIVectorizerParameters(
                        resource_url=self.aoai_endpoint,
                        deployment_name=self.embedding_deployment_name,
                        model_name=self.embedding_model_name,
                        api_key=self.aoai_key,  # local authentication
                    )
                )
            ]
        )

        # Create search index
        index = SearchIndex(name=self.index_name, fields=fields, vector_search=vector_search)
        result = index_client.create_or_update_index(index)
        print(f"{result.name} created")

    def create_data_source(self):
        """
        Create or update the Azure Search data source connection to Azure Blob Storage.
        """
        indexer_client = SearchIndexerClient(endpoint=self.endpoint, credential=self.credential)
        container = SearchIndexerDataContainer(name=self.blob_container_name)
        
        connection_string = (  # key based authentication
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={self.storage_account_name};"
            f"AccountKey={self.storage_account_key};"
            f"EndpointSuffix=core.windows.net"
        )
        
        data_source_connection = SearchIndexerDataSourceConnection(
            name=self.data_source_name,
            type="azureblob",
            connection_string=connection_string,  # or use storage_account_connection_string (with MI)
            container=container
        )
        
        data_source = indexer_client.create_or_update_data_source_connection(data_source_connection)
        print(f"Data source '{data_source.name}' created or updated")
    
    def create_indexer(self):
        """
        Create or update the Azure Search indexer to connect the data source and index.
        """
        indexer = SearchIndexer(
            name=self.indexer_name,
            description="Indexer to index documents and generate embeddings",
            skillset_name=self.skillset_name,  # skill set
            target_index_name=self.index_name,  # destination
            data_source_name=self.data_source_name,  # origin
            field_mappings=[
                FieldMapping(source_field_name="metadata_storage_name", target_field_name="title")
            ]
        )
        
        indexer_client = SearchIndexerClient(endpoint=self.endpoint, credential=self.credential)
        indexer_result = indexer_client.create_or_update_indexer(indexer)
        print(f"{indexer_result.name} created and running. Give the indexer a few minutes before running a query.")

    def create_skillset(self):
        """
        Create a skillset to chunk documents and generate embeddings.
        """
        split_skill = self.get_chunking_skill()
        embedding_skill = self.get_embedding_skill()
        index_projections = self.get_projections()

        skills = [split_skill, embedding_skill]
        skillset = SearchIndexerSkillset(
            name=self.skillset_name,
            description="Skillset to chunk docs and generate embeddings (key‑based)",
            skills=skills,
            index_projection=index_projections
        )

        self.client = SearchIndexerClient(endpoint=self.endpoint, credential=self.credential)
        self.client.create_or_update_skillset(skillset)
        print(f"{skillset.name} created (key-based)")


    # Helper methods to create skills and projections
    def get_chunking_skill(self):
        """
        Create a skill to chunk documents into pages.
        """
        return SplitSkill(
            description="Split skill to chunk documents",
            text_split_mode="pages",
            context="/document",
            maximum_page_length=1000,
            page_overlap_length=300,
            inputs=[
                InputFieldMappingEntry(name="text", source="/document/content"),
            ],
            outputs=[
                OutputFieldMappingEntry(name="textItems", target_name="pages")
            ]
        )

    def get_embedding_skill(self):
        """
        Create a skill to generate embeddings using Azure OpenAI.
        """
        return AzureOpenAIEmbeddingSkill(
            description="Skill to generate embeddings via Azure OpenAI (key‑based)",
            context="/document/pages/*",
            resource_url=self.aoai_endpoint,
            deployment_name=self.embedding_deployment_name,
            model_name=self.embedding_model_name,
            dimensions=self.embedding_model_dimensions,
            api_key=self.aoai_key,  # Azure OpenAI key (temporary workaround local authentication)
            inputs=[
                InputFieldMappingEntry(name="text", source="/document/pages/*"),
            ],
            outputs=[
                OutputFieldMappingEntry(name="embedding", target_name="text_vector")
            ]
        )

    def get_projections(self):
        """
        Create projections to handle parent-child relationships in the index.
        """
        return SearchIndexerIndexProjection(
            selectors=[
                SearchIndexerIndexProjectionSelector(
                    target_index_name=self.index_name,
                    parent_key_field_name="parent_id",
                    source_context="/document/pages/*",
                    mappings=[
                        InputFieldMappingEntry(name="chunk", source="/document/pages/*"),
                        InputFieldMappingEntry(name="text_vector", source="/document/pages/*/text_vector"),
                        InputFieldMappingEntry(name="title", source="/document/metadata_storage_name"),
                    ],
                ),
            ],
            parameters=SearchIndexerIndexProjectionsParameters(
                projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS
            )
        )


if __name__ == "__main__":
    search_setup = SearchSetupBlob()
    search_setup.create_search_index()
    search_setup.create_data_source()
    search_setup.create_skillset()
    search_setup.create_indexer()
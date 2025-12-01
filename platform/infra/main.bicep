// ========== main.bicep ========== //
metadata description = 'Resources for the Conversational Energy Management system.'
targetScope = 'resourceGroup'

@description('Name of the existing AI Search resource.')
param existing_search_service_name string
@description('Resource group where the existing search service is deployed.')
param existing_search_service_rg string

@description('Name of the existing Cosmos DB resource.')
param existing_cosmos_account_name string
@description('Resource group where the existing Cosmos DB service is deployed.')
param existing_cosmos_account_rg string

@description('Name of the existing Azure AI Foundry resource, for CLU, CQA authoring')
param existing_authoring_ai_foundry_name string
@description('Resource group where the existing Azure AI Foundry service is deployed.')
param existing_authoring_ai_foundry_rg string


// GPT model:
@description('Name of GPT model to deploy.')
@allowed([
  'gpt-4o-mini'
  'gpt-4o'
])
param gpt_model_name string

@description('Capacity of GPT model deployment.')
@minValue(1)
param gpt_deployment_capacity int

@description('GPT model deployment type.')
@allowed([
  'Standard'
  'GlobalStandard'
])
param gpt_deployment_type string

// Embedding model:
@description('Name of Embedding model to deploy.')
@allowed([
  'text-embedding-ada-002'
  'text-embedding-3-small'
])
param embedding_model_name string

@description('Capacity of embedding model deployment.')
@minValue(1)
param embedding_deployment_capacity int

@description('Embedding model deployment type.')
@allowed([
  'Standard'
  'GlobalStandard'
])
param embedding_deployment_type string

// Variables:
var suffix = uniqueString(subscription().id, resourceGroup().id, resourceGroup().location)

//----------- Deploy App Dependencies -----------//
module managed_identity 'resources/managed_identity.bicep' = {
  name: 'deploy_managed_identity'
  params: {
    suffix: suffix
  }
}

module storage_account 'resources/storage_account.bicep' = {
  name: 'deploy_storage_account'
  params: {
    suffix: suffix
  }
}

module cosmos_account 'resources/existing_cosmos_account.bicep' = {
  name: 'deploy_cosmos_account'
  params: {
    name: existing_cosmos_account_name
    existingResourceGroup: existing_cosmos_account_rg
  }
}

// module search_service 'resources/search_service.bicep' = {
//   name: 'deploy_search_service'
//   params: {
//     suffix: suffix
//   }
// }

// Using an existing search service, instead of creating a new one
module search_service 'resources/existing_search.bicep' = {
  name: 'deploy_existing_search_service'
  params: {
    name: existing_search_service_name
    existingResourceGroup: existing_search_service_rg
  }
}

module ai_foundry 'resources/ai_foundry.bicep' = {
  name: 'deploy_ai_foundry'
  params: {
    suffix: suffix
    managed_identity_name: managed_identity.outputs.name
    search_service_name: search_service.outputs.name
    search_service_resource_group: existing_search_service_rg
    gpt_model_name: gpt_model_name
    gpt_deployment_capacity: gpt_deployment_capacity
    gpt_deployment_type: gpt_deployment_type
    embedding_model_name: embedding_model_name
    embedding_deployment_capacity: embedding_deployment_capacity
    embedding_deployment_type: embedding_deployment_type

    existing_authoring_ai_foundry_name: existing_authoring_ai_foundry_name
    existing_authoring_ai_foundry_rg: existing_authoring_ai_foundry_rg
  }
}

// module ai_foundry 'resources/existing_ai_foundry.bicep' = {
//   name: 'deploy_ai_foundry'
//   params: {
//     suffix: suffix
//     name: existing_foundry_name
//     agents_project_name: existing_foundry_project_name
//     gpt_model_name: existing_gpt_model_name
//     embedding_model_name: existing_embedding_model_name
//     existing_resource_group: existing_ai_foundry_resource_group

//     managed_identity_name: managed_identity.outputs.name
//     location: resourceGroup().location
//     gpt_deployment_capacity: gpt_deployment_capacity
//     gpt_deployment_type: gpt_deployment_type
//     embedding_deployment_capacity: embedding_deployment_capacity
//     embedding_deployment_type: embedding_deployment_type
//     search_service_name: search_service.outputs.name
//     search_service_resource_group: existing_search_service_resource_group
//   }
// }

// module role_assignments 'resources/role_assignments.bicep' = {
//   name: 'create_role_assignments'
//   params: {
//     managed_identity_name: managed_identity.outputs.name
//     ai_foundry_name: ai_foundry.outputs.name
//     search_service_name: search_service.outputs.name
//     storage_account_name: storage_account.outputs.name
//   }
// }

//----------- Deploy App -----------//
module container_instance 'resources/container_instance.bicep' = {
  name: 'deploy_container_group'
  params: {
    suffix: suffix
    cosmos_endpoint: cosmos_account.outputs.endpoint
    cosmos_primary_key: cosmos_account.outputs.key
    agents_project_endpoint: ai_foundry.outputs.agents_project_endpoint
    aoai_deployment: ai_foundry.outputs.gpt_deployment_name
    aoai_endpoint: ai_foundry.outputs.openai_endpoint
    language_endpoint: ai_foundry.outputs.language_endpoint
    managed_identity_name: managed_identity.outputs.name
    search_endpoint: search_service.outputs.endpoint
    search_index_name: '${search_service.outputs.name}-conv-energy-index'
    blob_container_name: storage_account.outputs.blob_container_name
    embedding_deployment_name: ai_foundry.outputs.embedding_deployment_name
    embedding_model_dimensions: ai_foundry.outputs.embedding_model_dimensions
    embedding_model_name: ai_foundry.outputs.embedding_model_name
    storage_account_connection_string: storage_account.outputs.connection_string
    storage_account_name: storage_account.outputs.name
  }
}

//----------- Outputs -----------//
// Azure Open AI
output AOAI_ENDPOINT string = ai_foundry.outputs.openai_endpoint
output AOAI_KEY string = ai_foundry.outputs.openai_key
output AOAI_DEPLOYMENT string = ai_foundry.outputs.gpt_deployment_name
output AGENTS_PROJECT_ENDPOINT string = ai_foundry.outputs.agents_project_endpoint
output EMBEDDING_DEPLOYMENT_NAME string = ai_foundry.outputs.embedding_deployment_name
output EMBEDDING_MODEL_NAME string = ai_foundry.outputs.embedding_model_name
output EMBEDDING_MODEL_DIMENSIONS int = ai_foundry.outputs.embedding_model_dimensions

// Storage Account
output STORAGE_ACCOUNT_CONNECTION_STRING string = storage_account.outputs.connection_string
output STORAGE_ACCOUNT_NAME string = storage_account.outputs.name
output STORAGE_ACCOUNT_KEY string = storage_account.outputs.key
output BLOB_CONTAINER_NAME string = storage_account.outputs.blob_container_name

// Cosmos DB
output AZURE_COSMOSDB_NAME string = cosmos_account.outputs.name
output AZURE_COSMOSDB_ENDPOINT string = cosmos_account.outputs.endpoint
output AZURE_COSMOSDB_KEY string = cosmos_account.outputs.key

// Azure AI Search
output SEARCH_ENDPOINT string = search_service.outputs.endpoint
output SEARCH_KEY string = search_service.outputs.key
output SEARCH_INDEX_NAME string = '${search_service.outputs.name}-conv-energy-index'
output SEARCH_INDEX_BLOB_NAME string = '${search_service.outputs.name}-conv-energy-index-blob'
output SEARCH_INDEX_COSMOS_NAME string = '${search_service.outputs.name}-conv-energy-index-cosmos'

// Azure AI Language
output LANGUAGE_ENDPOINT string = ai_foundry.outputs.language_endpoint
// not all regions support Language service authoring
output AUTHORING_LANGUAGE_ENDPOINT string = ai_foundry.outputs.authoring_language_endpoint
output AUTHORING_AOAI_KEY string = ai_foundry.outputs.authoring_openai_key

output CLU_PROJECT_NAME string = container_instance.outputs.clu_project_name
output CLU_DEPLOYMENT_NAME string = container_instance.outputs.clu_deployment_name
output CLU_MODEL_NAME string = container_instance.outputs.clu_model_name
output CLU_CONFIDENCE_THRESHOLD string = container_instance.outputs.clu_confidence_threshold

output CQA_PROJECT_NAME string = container_instance.outputs.cqa_project_name
output CQA_DEPLOYMENT_NAME string = container_instance.outputs.cqa_deployment_name
output CQA_CONFIDENCE_THRESHOLD string = container_instance.outputs.cqa_confidence_threshold

output ORCHESTRATION_PROJECT_NAME string = container_instance.outputs.orchestration_project_name
output ORCHESTRATION_DEPLOYMENT_NAME string = container_instance.outputs.orchestration_deployment_name
output ORCHESTRATION_MODEL_NAME string = container_instance.outputs.orchestration_model_name
output ORCHESTRATION_CONFIDENCE_THRESHOLD string = container_instance.outputs.orchestration_confidence_threshold

output PII_ENABLED string = container_instance.outputs.pii_enabled
output PII_CATEGORIES string = container_instance.outputs.pii_categories
output PII_CONFIDENCE_THRESHOLD string = container_instance.outputs.pii_confidence_threshold

// Managed Identity
output USE_MI_AUTH bool = false // bool, false for local runs (run az login beforehand)
output MI_CLIENT_ID string = managed_identity.outputs.id

// Other
output ROUTER_TYPE string = container_instance.outputs.router_type
output WEB_APP_URL string = container_instance.outputs.fqdn

@description('Resource name suffix.')
param suffix string

@description('Name of AI Foundry resource.')
param name string

@description('Location for all resources.')
param location string = resourceGroup().location

@description('Resource group where the existing AI Foundry account is deployed.')
param existing_resource_group string

@description('Agents AI Foundry project name.')
param agents_project_name string

// GPT model:
@description('Name of GPT model to deploy.')
param gpt_model_name string

@description('Capacity of GPT model deployment.')
@minValue(1)
param gpt_deployment_capacity int

@allowed([
  'Standard'
  'GlobalStandard'
])
param gpt_deployment_type string

// Embedding model:
@description('Name of embedding model to deploy.')
param embedding_model_name string

@description('Capacity of embedding model deployment.')
@minValue(1)
param embedding_deployment_capacity int

@description('Model dimensions of embedding model to deploy.')
param embedding_model_dimensions int = 1536

@allowed([
  'Standard'
  'GlobalStandard'
])
param embedding_deployment_type string

// Search service:
@description('Name of AI Search resource')
param search_service_name string

@description('Resource group where the existing search service is deployed.')
param search_service_resource_group string

resource search_service 'Microsoft.Search/searchServices@2023-11-01' existing = {
  name: search_service_name
  scope: resourceGroup(search_service_resource_group)
}

// Managed Identity:
@description('Name of managed identity to use for Container Apps.')
param managed_identity_name string

resource managed_identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: managed_identity_name
}

//----------- Reference Existing AI Foundry Account -----------//
resource ai_foundry 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: name
  scope: resourceGroup(existing_resource_group)
}

//----------- Reference Existing Agents Project -----------//
resource agents_project 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' existing = {
  parent: ai_foundry
  name: agents_project_name
}

//----------- Reference Existing GPT Deployment -----------//
resource gpt_deployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' existing = {
  parent: ai_foundry
  name: gpt_model_name
}

//----------- Reference Existing Embedding Deployment -----------//
resource embedding_deployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' existing = {
  parent: ai_foundry
  name: embedding_model_name
}

//----------- Outputs (unchanged) -----------//
var language_endpoint_key = 'Language'

output name string                                  = ai_foundry.name
output agents_project_endpoint string               = agents_project.properties.endpoints['AI Foundry API']
output language_endpoint string                     = ai_foundry.properties.endpoints[language_endpoint_key]
output openai_endpoint string                       = ai_foundry.properties.endpoints['OpenAI Language Model Instance API']
output gpt_deployment_name string                    = gpt_deployment.name
output embedding_deployment_name string              = embedding_deployment.name
output embedding_model_name string                   = embedding_deployment.properties.model.name
output embedding_model_dimensions int                = embedding_model_dimensions

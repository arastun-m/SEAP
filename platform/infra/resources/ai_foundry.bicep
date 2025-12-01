@description('Resource name suffix')
param suffix string

@description('Name of AI Foundry resource.')
param name string = 'aif-${suffix}'

param existing_authoring_ai_foundry_name string
param existing_authoring_ai_foundry_rg string

@description('Location for all resources.')
param location string = resourceGroup().location

@description('Agents AI Foundry project name.')
param agents_project_name string = '${name}-agents'

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

//----------- AI Foundry Resource -----------//
resource existing_authoring_ai_foundry 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: existing_authoring_ai_foundry_name
  scope: resourceGroup(existing_authoring_ai_foundry_rg)
}

resource ai_foundry 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: name
  location: location
  kind: 'AIServices'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    //restore: true
    allowProjectManagement: true
    disableLocalAuth: false // temporary workaround (need API key for indexer embedding skill)
    customSubDomainName: name
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      //bypass: 'AzureServices'
    }
    apiProperties: {
      qnaAzureSearchEndpointId: search_service.id
      qnaAzureSearchEndpointKey: search_service.listAdminKeys().primaryKey
    }
  }
  sku: {
    name: 'S0'
  }

  resource agents_project 'projects@2025-04-01-preview' = {
    name: agents_project_name
    location: location
    identity: {
      type: 'UserAssigned'
      userAssignedIdentities: {
        '${managed_identity.id}' : {}
      }
    }
    properties: {}
  }

  resource gpt_deployment 'deployments' = {
    name: gpt_model_name
    properties: {
      model: {
        format: 'OpenAI'
        name: gpt_model_name
      }
    }
    sku: {
      name: gpt_deployment_type
      capacity: gpt_deployment_capacity
    } 
  }

  resource embedding_deployment 'deployments' = {
    name: embedding_model_name
    properties: {
      model: {
        format: 'OpenAI'
        name: embedding_model_name
      }
    }
    sku: {
      name: embedding_deployment_type
      capacity: embedding_deployment_capacity
    }
    dependsOn: [
      gpt_deployment
    ]
  }
}

//----------- Outputs -----------//
var language_endpoint_key = 'Language'
output name string = ai_foundry.name
output agents_project_endpoint string = ai_foundry::agents_project.properties.endpoints['AI Foundry API']
output language_endpoint string = ai_foundry.properties.endpoints[language_endpoint_key]
output authoring_language_endpoint string = existing_authoring_ai_foundry.properties.endpoints[language_endpoint_key]
output openai_endpoint string = ai_foundry.properties.endpoints['OpenAI Language Model Instance API']
output openai_key string = listKeys(ai_foundry.id, '2025-04-01-preview').key1
output authoring_openai_key string = listKeys(existing_authoring_ai_foundry.id, '2025-04-01-preview').key1
output gpt_deployment_name string = ai_foundry::gpt_deployment.name
output embedding_deployment_name string = ai_foundry::embedding_deployment.name
output embedding_model_name string = ai_foundry::embedding_deployment.properties.model.name
output embedding_model_dimensions int = embedding_model_dimensions

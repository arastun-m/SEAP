@description('Resource name suffix.')
param suffix string

@description('Name of AI Search resource.')
param name string = 'srch-${suffix}'

@description('Location for all resources.')
param location string = resourceGroup().location

//----------- Search Service Resource -----------//
resource search_service 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: name
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    disableLocalAuth: false // CQA can only auth to search service using API key...
    semanticSearch: 'free'
    publicNetworkAccess: 'enabled'
    networkRuleSet: {
      bypass: 'AzureServices'
      ipRules: []
    }
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
  }
  sku: {
    name: 'basic'
  }
}

//----------- Outputs -----------//
output name string = search_service.name
output endpoint string = 'https://${search_service.name}.search.windows.net'

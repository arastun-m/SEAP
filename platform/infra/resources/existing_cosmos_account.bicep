@description('Name of the existing AI Search resource.')
param name string

@description('Resource group where the existing search service is deployed.')
param existingResourceGroup string

//----------- Reference Existing Cosmos DB Service -----------//
resource existing_cosmos_account 'Microsoft.DocumentDB/databaseAccounts@2024-11-15' existing = {
  name: name
  scope: resourceGroup(existingResourceGroup)
}

//----------- Outputs -----------//
output name string = existing_cosmos_account.name
output endpoint string = existing_cosmos_account.properties.documentEndpoint
output key string = listKeys(existing_cosmos_account.id, '2024-11-15').primaryMasterKey

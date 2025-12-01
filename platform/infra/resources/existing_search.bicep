@description('Name of the existing AI Search resource.')
param name string

@description('Resource group where the existing search service is deployed.')
param existingResourceGroup string

//----------- Reference Existing Search Service -----------//
resource existing_search_service 'Microsoft.Search/searchServices@2024-06-01-preview' existing = {
  name: name
  scope: resourceGroup(existingResourceGroup)
}

//----------- Outputs -----------//
output name string = existing_search_service.name
output endpoint string = 'https://${existing_search_service.name}.search.windows.net'
output key string = listAdminKeys(existing_search_service.id, '2024-06-01-preview').primaryKey

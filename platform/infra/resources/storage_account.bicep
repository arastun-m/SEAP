@description('Resource name suffix')
param suffix string

@description('Name of Storage Account resource.')
param name string = 'st${suffix}'

@description('Location for all resources.')
param location string = resourceGroup().location

@description('Blob container name.')
param blob_container_name string = 'energy-system-manuals'

//----------- Storage Account Resource -----------//
resource storage_account 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: name
  location: location
  kind: 'StorageV2'
  properties: {
    allowSharedKeyAccess: true
    allowBlobPublicAccess: false
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
  sku: {
    name: 'Standard_LRS'
  }

  resource blob_service 'blobServices' = {
    name: 'default'

    resource blob_container 'containers' = {
      name: blob_container_name
      properties: {
        publicAccess: 'None'
      }
    }
  }
}

//----------- Outputs -----------//
output name string = storage_account.name
output connection_string string = 'ResourceId=${storage_account.id};'
output blob_container_name string = storage_account::blob_service::blob_container.name
output key string = listKeys(storage_account.id, '2023-05-01').keys[0].value

using './main.bicep'

param gpt_model_name = readEnvironmentVariable('AZURE_ENV_GPT_MODEL_NAME', 'gpt-4o-mini')
param gpt_deployment_capacity = int(readEnvironmentVariable('AZURE_ENV_GPT_MODEL_CAPACITY', '100'))
param gpt_deployment_type = readEnvironmentVariable('AZURE_ENV_GPT_MODEL_DEPLOYMENT_TYPE', 'GlobalStandard')

param embedding_model_name = readEnvironmentVariable('AZURE_ENV_EMBEDDING_MODEL_NAME', 'text-embedding-ada-002')
param embedding_deployment_capacity = int(readEnvironmentVariable('AZURE_ENV_EMBEDDING_MODEL_CAPACITY', '100'))
param embedding_deployment_type = readEnvironmentVariable('AZURE_ENV_EMBEDDING_MODEL_DEPLOYMENT_TYPE', 'GlobalStandard')

// Existing resources
param existing_search_service_name = readEnvironmentVariable('AZURE_ENV_SEARCH_SERVICE_NAME', 'campus-connect')
param existing_search_service_rg = readEnvironmentVariable('AZURE_ENV_SEARCH_SERVICE_RESOURCE_GROUP', 'rg-dany.herscovitch-1831')
param existing_cosmos_account_name = readEnvironmentVariable('AZURE_ENV_COSMOS_ACCOUNT_NAME', 'campus-connect')
param existing_cosmos_account_rg = readEnvironmentVariable('AZURE_ENV_COSMOS_ACCOUNT_RESOURCE_GROUP', 'rg-dany.herscovitch-1831')

param existing_authoring_ai_foundry_name = readEnvironmentVariable('AZURE_ENV_AUTHORING_FOUNDARY_ACCOUNT', 'campus-energy-resource')
param existing_authoring_ai_foundry_rg = readEnvironmentVariable('AZURE_ENV_AUTHORING_FOUNDARY_RESOURCE_GROUP', 'rg-jzz24-6044')

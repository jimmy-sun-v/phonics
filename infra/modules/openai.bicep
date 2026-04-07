@description('Azure OpenAI account name')
param name string

param location string

@description('Model to deploy')
param modelName string

@description('Model version')
param modelVersion string

@description('Deployment capacity (thousands of tokens per minute)')
param capacity int

resource openai 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
  name: name
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
  parent: openai
  name: modelName
  sku: {
    name: 'Standard'
    capacity: capacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
}

output accountName string = openai.name
output endpoint string = openai.properties.endpoint
output key string = openai.listKeys().key1

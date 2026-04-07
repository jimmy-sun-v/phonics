@description('Speech Services account name')
param name string

param location string

@description('Pricing tier')
@allowed(['F0', 'S0'])
param sku string = 'F0'

resource speech 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
  name: name
  location: location
  kind: 'SpeechServices'
  sku: {
    name: sku
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

output accountName string = speech.name
output key string = speech.listKeys().key1
output endpoint string = speech.properties.endpoint

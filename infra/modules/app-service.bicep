@description('App Service Plan name')
param planName string

@description('Web App name')
param appName string

param location string

param logAnalyticsWorkspaceId string

@secure()
param databaseUrl string
@secure()
param speechKey string
param speechRegion string
@secure()
param openAiEndpoint string
@secure()
param openAiKey string
param openAiDeployment string
@secure()
param djangoSecretKey string
param sessionRetentionHours int

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  kind: 'linux'
  sku: {
    name: 'B1'
  }
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'startup.sh'
      alwaysOn: true
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      healthCheckPath: '/health/'
      appSettings: [
        { name: 'DJANGO_SETTINGS_MODULE', value: 'config.settings.prod' }
        { name: 'SECRET_KEY', value: djangoSecretKey }
        { name: 'ALLOWED_HOSTS', value: '${appName}.azurewebsites.net' }
        { name: 'DATABASE_URL', value: databaseUrl }
        { name: 'AZURE_SPEECH_KEY', value: speechKey }
        { name: 'AZURE_SPEECH_REGION', value: speechRegion }
        { name: 'AZURE_OPENAI_ENDPOINT', value: openAiEndpoint }
        { name: 'AZURE_OPENAI_API_KEY', value: openAiKey }
        { name: 'AZURE_OPENAI_DEPLOYMENT', value: openAiDeployment }
        { name: 'AZURE_OPENAI_API_VERSION', value: '2024-06-01' }
        { name: 'SESSION_RETENTION_HOURS', value: string(sessionRetentionHours) }
        { name: 'SCM_DO_BUILD_DURING_DEPLOYMENT', value: 'true' }
      ]
    }
  }
}

resource diagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${appName}-diag'
  scope: webApp
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        category: 'AppServiceHTTPLogs'
        enabled: true
      }
      {
        category: 'AppServiceAppLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

output appName string = webApp.name
output defaultHostname string = 'https://${webApp.properties.defaultHostName}'

targetScope = 'resourceGroup'

@description('Environment name used as a suffix for resource names')
@allowed(['dev', 'staging', 'prod'])
param environmentName string

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Base name for the application')
param appName string

@description('PostgreSQL administrator login')
param dbAdminLogin string

@secure()
@description('PostgreSQL administrator password')
param dbAdminPassword string

@description('Speech Services SKU (F0 = free, S0 = standard)')
@allowed(['F0', 'S0'])
param speechSku string = 'F0'

@description('OpenAI model to deploy')
param openAiModelName string = 'gpt-4o-mini'

@description('Model version')
param openAiModelVersion string = '2024-07-18'

@description('OpenAI deployment capacity in thousands of tokens per minute')
param openAiCapacity int = 10

@secure()
@description('Django SECRET_KEY')
param djangoSecretKey string

@description('Session retention in hours')
param sessionRetentionHours int = 24

var suffix = '${appName}-${environmentName}'

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    name: 'log-${suffix}'
    location: location
  }
}

module database 'modules/database.bicep' = {
  name: 'database'
  params: {
    serverName: 'psql-${suffix}'
    databaseName: 'phonicsapp'
    location: location
    adminLogin: dbAdminLogin
    adminPassword: dbAdminPassword
  }
}

module speech 'modules/speech.bicep' = {
  name: 'speech'
  params: {
    name: 'speech-${suffix}'
    location: location
    sku: speechSku
  }
}

module openai 'modules/openai.bicep' = {
  name: 'openai'
  params: {
    name: 'openai-${suffix}'
    location: location
    modelName: openAiModelName
    modelVersion: openAiModelVersion
    capacity: openAiCapacity
  }
}

module appService 'modules/app-service.bicep' = {
  name: 'appService'
  params: {
    planName: 'plan-${suffix}'
    appName: 'app-${suffix}'
    location: location
    logAnalyticsWorkspaceId: monitoring.outputs.workspaceId
    databaseUrl: 'postgres://${dbAdminLogin}:${dbAdminPassword}@${database.outputs.fqdn}:5432/phonicsapp?sslmode=require'
    speechKey: speech.outputs.key
    speechRegion: location
    openAiEndpoint: openai.outputs.endpoint
    openAiKey: openai.outputs.key
    openAiDeployment: openAiModelName
    djangoSecretKey: djangoSecretKey
    sessionRetentionHours: sessionRetentionHours
  }
}

output appServiceName string = appService.outputs.appName
output appUrl string = appService.outputs.defaultHostname
output postgresqlFqdn string = database.outputs.fqdn
output speechAccountName string = speech.outputs.accountName
output openAiAccountName string = openai.outputs.accountName

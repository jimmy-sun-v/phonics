using './main.bicep'

param environmentName = 'dev'
param location = 'eastus'
param appName = 'phonics-tutor'
// param dbAdminLogin = 'phonicsadmin'
param speechSku = 'F0'
param openAiModelName = 'gpt-4.1-mini'
param openAiModelVersion = '2025-04-14'
param openAiCapacity = 10
// param sessionRetentionHours = 24

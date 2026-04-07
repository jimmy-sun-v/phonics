using './main.bicep'

param environmentName = 'dev'
param location = 'eastus'
param appName = 'phonics-tutor'
param dbAdminLogin = 'phonicsadmin'
param speechSku = 'F0'
param openAiModelName = 'gpt-4o-mini'
param openAiModelVersion = '2024-07-18'
param openAiCapacity = 10
param sessionRetentionHours = 24

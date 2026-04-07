# Design: Task 7.0 – Infrastructure as Code (Bicep)

## Overview

Define all Azure infrastructure in declarative Bicep templates, replacing the ad-hoc CLI commands scattered across Tasks 7.1–7.3 and 8.1. A single `az deployment` command provisions every resource, wires secrets into App Service settings, and enables Easy Auth — making deployments repeatable, version-controlled, and idempotent.

## Dependencies

- All previous phases complete (infrastructure is deployed last)

## Detailed Design

### Resources Provisioned

| Resource | Bicep Type | SKU | Purpose |
|----------|-----------|-----|---------|
| App Service Plan | `Microsoft.Web/serverfarms` | B1 (Linux) | Host web app |
| App Service | `Microsoft.Web/sites` | Linux Python 3.11 | Django application |
| PostgreSQL Flexible Server | `Microsoft.DBforPostgreSQL/flexibleServers` | Burstable B1ms | Database |
| PostgreSQL Database | `Microsoft.DBforPostgreSQL/flexibleServers/databases` | — | App database |
| Cognitive Services (Speech) | `Microsoft.CognitiveServices/accounts` | F0 / S0 | STT + TTS |
| Cognitive Services (OpenAI) | `Microsoft.CognitiveServices/accounts` | S0 | LLM feedback |
| OpenAI Model Deployment | `Microsoft.CognitiveServices/accounts/deployments` | Standard (10 capacity) | gpt-4o-mini |
| Log Analytics Workspace | `Microsoft.OperationalInsights/workspaces` | PerGB2018 | Centralised logging |

### File Layout

```
PhonicsApp/
└── infra/
    ├── main.bicep              # Orchestrator – references all modules
    ├── main.bicepparam         # Default parameter values
    ├── modules/
    │   ├── app-service.bicep   # App Service Plan + Web App + settings
    │   ├── database.bicep      # PostgreSQL Flexible Server + database
    │   ├── speech.bicep        # Cognitive Services Speech
    │   ├── openai.bicep        # Cognitive Services OpenAI + model deployment
    │   └── monitoring.bicep    # Log Analytics workspace
    └── README.md               # Deployment instructions
```

### Parameters

**File: `infra/main.bicepparam`**

```
using './main.bicep'

param environmentName = 'dev'
param location = 'eastus'
param appName = 'phonics-tutor'

// PostgreSQL
param dbAdminLogin = 'phonicsadmin'
// dbAdminPassword should be supplied at deployment time via --parameters or a Key Vault reference

// Speech Services
param speechSku = 'F0'   // F0 for dev, S0 for prod

// OpenAI
param openAiModelName = 'gpt-4o-mini'
param openAiModelVersion = '2024-07-18'
param openAiCapacity = 10

// App
param djangoSecretKey = ''  // supply at deployment time
```

---

### Bicep Modules

#### `infra/main.bicep`

```bicep
targetScope = 'resourceGroup'

@description('Environment name used as a suffix for resource names')
@allowed(['dev', 'staging', 'prod'])
param environmentName string

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Base name for the application')
param appName string

// --- Database params ---
@description('PostgreSQL administrator login')
param dbAdminLogin string

@secure()
@description('PostgreSQL administrator password')
param dbAdminPassword string

// --- Speech params ---
@description('Speech Services SKU (F0 = free, S0 = standard)')
@allowed(['F0', 'S0'])
param speechSku string = 'F0'

// --- OpenAI params ---
@description('OpenAI model to deploy')
param openAiModelName string = 'gpt-4o-mini'

@description('Model version')
param openAiModelVersion string = '2024-07-18'

@description('OpenAI deployment capacity in thousands of tokens per minute')
param openAiCapacity int = 10

// --- App params ---
@secure()
@description('Django SECRET_KEY')
param djangoSecretKey string

@description('Session retention in hours')
param sessionRetentionHours int = 24

// ───────────────────────────────────────────────
// Resource name helper
// ───────────────────────────────────────────────
var suffix = '${appName}-${environmentName}'

// ───────────────────────────────────────────────
// Modules
// ───────────────────────────────────────────────

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
    // Database
    databaseUrl: 'postgres://${dbAdminLogin}:${dbAdminPassword}@${database.outputs.fqdn}:5432/phonicsapp?sslmode=require'
    // Speech
    speechKey: speech.outputs.key
    speechRegion: location
    // OpenAI
    openAiEndpoint: openai.outputs.endpoint
    openAiKey: openai.outputs.key
    openAiDeployment: openAiModelName
    // App
    djangoSecretKey: djangoSecretKey
    sessionRetentionHours: sessionRetentionHours
  }
}

// ───────────────────────────────────────────────
// Outputs
// ───────────────────────────────────────────────

output appServiceName string = appService.outputs.appName
output appUrl string = appService.outputs.defaultHostname
output postgresqlFqdn string = database.outputs.fqdn
output speechAccountName string = speech.outputs.accountName
output openAiAccountName string = openai.outputs.accountName
```

#### `infra/modules/app-service.bicep`

```bicep
@description('App Service Plan name')
param planName string

@description('Web App name')
param appName string

param location string

param logAnalyticsWorkspaceId string

// --- App settings passed from main ---
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

// ───────────────────────────────────────────────

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  kind: 'linux'
  sku: {
    name: 'B1'
  }
  properties: {
    reserved: true  // required for Linux
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
```

#### `infra/modules/database.bicep`

```bicep
@description('PostgreSQL Flexible Server name')
param serverName string

@description('Database name')
param databaseName string

param location string

@description('Administrator login')
param adminLogin string

@secure()
@description('Administrator password')
param adminPassword string

// ───────────────────────────────────────────────

resource server 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: serverName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '16'
    administratorLogin: adminLogin
    administratorLoginPassword: adminPassword
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }
}

// Allow Azure services to connect (App Service → PostgreSQL)
resource firewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-12-01-preview' = {
  parent: server
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Require SSL
resource sslConfig 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-12-01-preview' = {
  parent: server
  name: 'require_secure_transport'
  properties: {
    value: 'on'
    source: 'user-override'
  }
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-12-01-preview' = {
  parent: server
  name: databaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

output fqdn string = server.properties.fullyQualifiedDomainName
output serverName string = server.name
```

#### `infra/modules/speech.bicep`

```bicep
@description('Speech Services account name')
param name string

param location string

@description('Pricing tier')
@allowed(['F0', 'S0'])
param sku string = 'F0'

// ───────────────────────────────────────────────

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
```

#### `infra/modules/openai.bicep`

```bicep
@description('Azure OpenAI account name')
param name string

param location string

@description('Model to deploy')
param modelName string

@description('Model version')
param modelVersion string

@description('Deployment capacity (thousands of tokens per minute)')
param capacity int

// ───────────────────────────────────────────────

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
```

#### `infra/modules/monitoring.bicep`

```bicep
@description('Log Analytics workspace name')
param name string

param location string

// ───────────────────────────────────────────────

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: name
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

output workspaceId string = workspace.id
output workspaceName string = workspace.name
```

---

### Deployment Commands

All commands are run from the repository root.

**1. Create Resource Group** (one-time, not in Bicep since it scopes the deployment):

```bash
az group create --name rg-phonics-app-dev --location eastus
```

**2. Deploy all infrastructure:**

```bash
az deployment group create \
    --resource-group rg-phonics-app-dev \
    --template-file infra/main.bicep \
    --parameters infra/main.bicepparam \
    --parameters dbAdminPassword='<strong-password>' \
                 djangoSecretKey='<generated-secret>'
```

**3. Deploy application code** (unchanged from Task 7.1):

```bash
az webapp up \
    --name app-phonics-tutor-dev \
    --resource-group rg-phonics-app-dev
```

**4. Tear down an environment:**

```bash
az group delete --name rg-phonics-app-dev --yes --no-wait
```

### Multi-Environment Support

Create additional parameter files per environment:

| File | `environmentName` | `speechSku` | Notes |
|------|-------------------|-------------|-------|
| `main.bicepparam` | `dev` | `F0` | Default dev |
| `prod.bicepparam` | `prod` | `S0` | Production |

Deploy to production:

```bash
az deployment group create \
    --resource-group rg-phonics-app-prod \
    --template-file infra/main.bicep \
    --parameters infra/prod.bicepparam \
    --parameters dbAdminPassword='<prod-password>' \
                 djangoSecretKey='<prod-secret>'
```

### What-If (Dry Run)

Preview changes before applying:

```bash
az deployment group what-if \
    --resource-group rg-phonics-app-dev \
    --template-file infra/main.bicep \
    --parameters infra/main.bicepparam \
    --parameters dbAdminPassword='<pw>' djangoSecretKey='<sk>'
```

---

## Acceptance Criteria

- [ ] All Bicep files compile without errors (`az bicep build --file infra/main.bicep`)
- [ ] `az deployment group create` provisions all resources in a single command
- [ ] Re-running the deployment is idempotent (no errors, no duplicate resources)
- [ ] App Service starts and `/health/` returns 200 after deployment
- [ ] All secrets (DB password, Django secret key, API keys) flow from Bicep params/outputs into App Settings — never hard-coded
- [ ] `what-if` correctly previews changes
- [ ] A second environment (e.g. `staging`) can be stood up using a different parameter file
- [ ] Teardown via `az group delete` removes all resources cleanly

## Test Strategy

- Validation: `az bicep build --file infra/main.bicep` compiles without errors
- Validation: `az deployment group what-if` shows expected resource list
- Integration: Deploy to a test resource group → verify all resources created in Azure Portal
- Integration: Deploy again → verify idempotent (no changes applied)
- Integration: Deploy app code → `/health/` returns 200
- Manual: Verify App Settings contain correct values from Bicep outputs
- Manual: Delete resource group → confirm clean teardown

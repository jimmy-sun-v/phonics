# Infrastructure Deployment

## Prerequisites

- Azure CLI installed and logged in (`az login`)
- Bicep CLI (`az bicep install`)

## Deploy

### 1. Create Resource Group

```bash
az group create --name rg-phonics-app-dev --location eastus
```

### 2. Deploy All Infrastructure

```bash
az deployment group create \
    --resource-group rg-phonics-app-dev \
    --template-file infra/main.bicep \
    --parameters infra/main.bicepparam \
    --parameters dbAdminPassword='<strong-password>' \
                 djangoSecretKey='<generated-secret>'
```

If just to test locally, no need to deploy DB, web App, App insights, but only Speech service and OpenAI LLM

```bash
az deployment group create \
    --resource-group rg-phonics-app-dev \
    --template-file infra/main.bicep \
    --parameters infra/main.bicepparam
```

### 3. Deploy Application Code

```bash
az webapp up \
    --name app-phonics-tutor-dev \
    --resource-group rg-phonics-app-dev
```

### 4. Preview Changes (What-If)

```bash
az deployment group what-if \
    --resource-group rg-phonics-app-dev \
    --template-file infra/main.bicep \
    --parameters infra/main.bicepparam \
    --parameters dbAdminPassword='<pw>' djangoSecretKey='<sk>'
```

### 5. Tear Down

```bash
az group delete --name rg-phonics-app-dev --yes --no-wait
```

## Multi-Environment

Create additional `.bicepparam` files for staging/production with different `environmentName` and SKU values.

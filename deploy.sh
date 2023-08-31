resource_group=teams_chatgpt
app_name=chimei-chat
app_plan_name=ASP-TeamsChatGPT-9637
acr_name=chimeiapiacr
acr_url=chimeiapiacr.azurecr.io
image_name=chimeiapiacr.azurecr.io/fastapi-demo:latest


# Create an Azure Container Registry with the az acr create command.
az acr create --resource-group $resource_group \
    --name $acr_name --sku Basic --admin-enabled true

ACR_PASSWORD=$(az acr credential show \
    --resource-group $resource_group \
    --name $acr_name \
    --query "passwords[?name == 'password'].value" \
    --output tsv)

# Push the Docker image to the Azure Container Registry created from the Dockerfile in the current directory.
az acr build --image fastapi-demo \
  --registry $acr_name \
  --file Dockerfile .

# Create an App Service plan with the az appservice plan command.
az appservice plan create \
    --name $app_name \
    --resource-group $resource_group \
    --sku B1 \
    --is-linux

# Deploy the container image to Azure App Service.
az webapp create \
    --name $app_name \
    --resource-group $resource_group \
    --plan $app_plan_name \
    --docker-registry-server-password $ACR_PASSWORD \
    --docker-registry-server-user $acr_name \
    --role acrpull \
    --deployment-container-image-name $image_name

# Deploy the container image to an exsisiting Azure App Service.
az webapp config container set \
  --name $app_name \
  --resource-group $resource_group \
  --docker-custom-image-name $image_name \
  --docker-registry-server-url $acr_url \
  --docker-registry-server-user $acr_name \
  --docker-registry-server-password $ACR_PASSWORD \
  --verbose
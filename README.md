# AOAI Chat GPT API

This project provides an API for interacting with the AOAI Chatbot. It uses FastAPI and OpenAI's gpt-35-turbo-16k API to facilitate conversations with the chatbot. The API allows users to send their queries and receive responses from the chatbot.

## Features

- Supports caching of chat histories in Redis to maintain conversation context.
- Provides CORS middleware to allow cross-origin requests.
- Gzip middleware is enabled for efficient response compression.

## Installation

1. Clone this repository.
2. Install the required dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
    ```

## Usage
1. Run the FastAPI application:

    ```bash
    uvicorn main:app --port 8000
    ```
2. Access the API docs at `http://127.0.0.1:8000/docs`
3. Use the `/getChatGptMessage` endpoint to interact with the chatbot. Send a POST request with the following JSON payload structure:
   ```json
   {
    "user_query": "Hello, how can you assist me?",
    "user_id": "1",
    "max_response": 7000,
    "temperature": 0.7,
    "top_p": 1,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stop_sequence": ""
    }
    ```
## Configuration
All the credentials can be configured in `config.py`. You can modify the `ChatCacheCount` to change the number of chat histories to be cached. The default value is 3.

## Deploy by Azure Pipeline
The API can be deployed to Azure App Service using Docker. This project implements CI/CD process with Azure Pipeline to auto deploy the API to Azure App Service whenever a new commit is pushed to the `main` branch of the [repository](https://dev.azure.com/aceraeb/TestForAndy/_git/pipelines-fastapi-docker). The pipeline is defined in `azure-pipelines.yml`.

## Deploy by Azure CLI
You can also build the docker image and push it to Azure Container Registry. Then, it will deploy the image to Azure App Service. The script is defined in `deploy.sh`.

## Reference

**Azure OpenAI completions example**
- https://github.com/openai/openai-python#microsoft-azure-endpoints
- https://platform.openai.com/docs/api-reference/chat/create

**Deploy FastAPI to App Service**
- By docker
  1. **Push image from a Dockerfile to Azure Container Registry**
       - https://learn.microsoft.com/en-us/azure/container-registry/container-registry-quickstart-task-cli
  2. ****Deploy image to app service (new/existing)****
       - https://learn.microsoft.com/en-us/azure/developer/python/tutorial-containerize-simple-web-app-for-app-service?tabs=web-app-fastapi
       - https://learn.microsoft.com/en-US/cli/azure/webapp/config/container?view=azure-cli-latest#az-webapp-config-container-set
- By python script
    - https://www.youtube.com/watch?v=oLdEI3zUcFg
- By Azure Pipeline (Docker)
    - https://learn.microsoft.com/en-us/azure/app-service/deploy-azure-pipelines?tabs=yaml
    - https://learn.microsoft.com/en-us/azure/devops/pipelines/apps/cd/deploy-docker-webapp?view=azure-devops&tabs=java%2Cyaml
    - https://www.youtube.com/watch?v=7qyWriiUenw

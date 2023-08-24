from fastapi import APIRouter, HTTPException, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from config import *
import redis
import openai
import json

openai.api_type = "azure"
openai.api_key = AoaiConfig["AoaiKeyCredential"]
openai.api_base = AoaiConfig["AoaiEndpointUrl"]
openai.api_version = "2023-05-15"


class RequestChatData(BaseModel):
   user_query: str
   user_id: str
   max_response: int
   temperature: float
   top_p: float
   frequency_penalty: float
   presence_penalty: float
   stop_sequence: str

class ChatReadCacheApproach():
   def __init__(self, 
                chatgpt_deployment: str, 
                request_chat_data: RequestChatData,
                redis_config: dict,
                chat_config: dict) -> None:
      self.chatgpt_deployment = chatgpt_deployment
      self.request_chat_data = request_chat_data
      self.redis_host = redis_config["Host"]
      self.redis_pwd = redis_config["Password"]
      self.chat_config = chat_config
      self.history = [{"role": "system", "content": "You are a helpful assistant."}]

   def run(self) -> any:
      try:
         redis_client = redis.StrictRedis(host=self.redis_host, port=6380, db=0, password=self.redis_pwd, ssl=True)
         user_id = self.request_chat_data.user_id
         # Check if the user has a history in Redis
         if redis_client.exists(user_id):
            # Retrieve and extend saved history from Redis
            saved_history = redis_client.get(user_id)
            if saved_history:
               saved_history = saved_history.decode("utf-8")
               self.history.clear()
               self.history.extend(self.parse_cache_to_history(json.loads(saved_history)))
         
         # Add the user's question to the history
         self.history.append({"role": "user", "content": self.request_chat_data.user_query})
         # Call the OpenAI API
         response = openai.ChatCompletion.create(
            deployment_id=AoaiConfig["AoaiChatGptDeployName"],
            messages=self.history,
            max_tokens=self.request_chat_data.max_response if self.request_chat_data.max_response else self.chat_config["MaxTokens"],
            temperature=self.request_chat_data.temperature if self.request_chat_data.temperature else self.chat_config["Temperature"],
            top_p=self.request_chat_data.top_p if self.request_chat_data.top_p else 1,
            frequency_penalty=self.request_chat_data.frequency_penalty if self.request_chat_data.frequency_penalty else 0,
            presence_penalty=self.request_chat_data.presence_penalty if self.request_chat_data.presence_penalty else 0,
            stop=self.request_chat_data.stop_sequence if self.request_chat_data.stop_sequence else None
         )  

         # Add the response to the history
         self.history.append({"role": response.choices[0].message.role, "content": response.choices[0].message.content})
         # Save the current history to Redis according to below format
         history_cache = self.parse_history_to_cache(self.history)
         # Serialize the history list to a JSON string and save it in Redis
         cache_num = self.chat_config["ChatCacheCount"]
         redis_client.set(user_id, json.dumps(history_cache[-cache_num:]))
         # Return the response
         return response.choices[0].message.content
      
      except Exception as e:
         print(e)
         raise HTTPException(status_code=500, detail="Internal Server Error")

   def reset_cache(self) -> None:
      redis_client = redis.StrictRedis(host=self.redis_host, port=6380, db=0, password=self.redis_pwd, ssl=True)
      redis_client.delete(self.request_chat_data.user_id)

   def parse_cache_to_history(self, cache: list) -> list:
      history = []
      for i in range(len(cache)):
         for key, value in cache[i].items():
            history.append({"role": "user", "content": key})
            history.append({"role": "assistant", "content": value})
      return history
   
   def parse_history_to_cache(self, history: list) -> list:
      # Format: {"Where was it played?": "It was played in the United States."}
      history_cache = []
      for i in range(len(history)):
         if history[i]["role"] == "user":
            history_cache.append({history[i]["content"]:history[i+1]["content"]})
      return history_cache


app = FastAPI(title="AOAI Chat GPT API (deployed with Azure Pipelines)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(GZipMiddleware)


@app.post("/getChatGptMessage", status_code = status.HTTP_201_CREATED)
def getChatGptMessage(requestChatData: RequestChatData):
   chat_read_cache_approach = ChatReadCacheApproach(AoaiConfig["AoaiChatGptDeployName"], requestChatData, RedisConfig, ChatConfig)
   response = chat_read_cache_approach.run()
   print(response)
   return response

# redis_client = redis.StrictRedis(host=RedisConfig["Host"], port=6380, db=0, password=RedisConfig["Password"], ssl=True)
# redis_client.flushall()
import asyncio
import json
import logging
import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

from appConfig import azure_round_robin_json_list

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv(verbose=True)

deployment_name = os.getenv("aoai_llm_deployment_name")
api_version = os.getenv("aosi_llm_api_version")

class AzureOpenAIClientsRoundRobin:
    def __init__(self):
        self.clients = []
        if azure_round_robin_json_list is not None:
            azure_round_robin = json.loads(azure_round_robin_json_list)
            for azure_openai in azure_round_robin:
                self.clients.append(
                    AzureChatOpenAI(
                        api_key=azure_openai["aozai_api_key"],  
                        api_version=api_version,
                        azure_deployment=deployment_name,
                        azure_endpoint=azure_openai["aoai_resource_uri"]))

            self.client_count = len(self.clients)
            self.index = 0  # init
            self.lock = asyncio.Lock()
    
    async def get_next_client(self):
        async with self.lock: 
            # get client
            client = self.clients[self.index]
            # update index 
            self.index = (self.index + 1) % self.client_count
            return client

# init client
client_manager = AzureOpenAIClientsRoundRobin()

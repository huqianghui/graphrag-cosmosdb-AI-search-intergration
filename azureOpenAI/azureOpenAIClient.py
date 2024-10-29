import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

from .azureOpenAIClientRoundRobin import client_manager

# 加载 .env 文件
load_dotenv()

resource_uri=os.getenv("aoai_resource_uri")
embedding_deployment_name=os.getenv("aoai_embedding_deployment_name")
llm_deployment_name = os.getenv("aoai_llm_deployment_name")
api_key= os.getenv("aozai_api_key")
api_version="2024-02-01"

def get_embdding_async_client():
    return AsyncAzureOpenAI(
        azure_endpoint=resource_uri, 
        azure_deployment=embedding_deployment_name,
        api_version=api_version, 
        api_key= api_key)

def get_azureOpenAI_async_client():
    return AsyncAzureOpenAI(
        azure_endpoint=resource_uri, 
        azure_deployment=llm_deployment_name,
        api_version=api_version, 
        api_key= api_key)

async def get_langchain_openai_client():
    return  await client_manager.get_next_client()


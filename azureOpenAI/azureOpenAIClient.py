import os

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

# 加载 .env 文件
load_dotenv()

resource_uri=os.getenv("aoai_resource_uri")
embedding_deployment_name=os.getenv("aoai_embedding_deployment_name")
llm_deployment_name = os.getenv("aoai_llm_deployment_name")
api_key= os.getenv("aozai_api_key")

def get_embdding_async_client():
    return AsyncAzureOpenAI(
        azure_endpoint=resource_uri, 
        azure_deployment=embedding_deployment_name,
        api_version="2024-02-01", 
        api_key= api_key)

def get_azureOpenAI_async_client():
    return AsyncAzureOpenAI(
        azure_endpoint=resource_uri, 
        azure_deployment=llm_deployment_name,
        api_version="2024-02-01", 
        api_key= api_key)



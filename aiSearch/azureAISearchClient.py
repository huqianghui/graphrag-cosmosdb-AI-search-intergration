import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient as searchClient
from azure.search.documents.aio import SearchClient as asyncSearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import QueryType, VectorizedQuery
from dotenv import load_dotenv

from azureOpenAI.azureOpenAIClient import (
    embedding_deployment_name,
    get_embdding_async_client,
)

# 加载 .env 文件
load_dotenv()

from .dataModel import Entity

search_creds = AzureKeyCredential(os.getenv("ai_search_key"))
search_endpoint = os.getenv("ai_search_endpoint")
index_name = os.getenv("ai_search_index_name")


def get_asyc_search_client():
    return asyncSearchClient(
        endpoint=search_endpoint, 
        credential=search_creds, 
        index_name=index_name)

def get_search_client():
    return searchClient(
        endpoint=search_endpoint, 
        credential=search_creds, 
        index_name=index_name)

def get_index_client():
    index_client = SearchIndexClient(endpoint=search_endpoint, credential=search_creds)
    return index_client

async def get_search_top_entities_by_text(query_text)->list[Entity]:
    asycEmbeedingClient = get_embdding_async_client()
    aoaiResponse = await asycEmbeedingClient.embeddings.create(input = query_text,model=embedding_deployment_name)  
    aoai_embedding_query = aoaiResponse.data[0].embedding

    aoai_embedding_query = VectorizedQuery(vector=aoai_embedding_query, 
                                k_nearest_neighbors=3, 
                                fields="description_embedding")

    searchAsycClient = get_asyc_search_client()

    # TODO query language is not supported for aiohttp version
    results = await searchAsycClient.search(  
        search_text=query_text,
        search_fields=["name","description","type"],
        #query_language="zh-cn",
        vector_queries=[aoai_embedding_query],
        query_type=QueryType.SEMANTIC, 
        semantic_configuration_name='default', 
        select=["id","name", "description","type","human_readable_id"],
        top=10
    )

    return results

async def get_search_top_entity_ids_by_entity_result(entity_result:list[Entity])->str:
    entity_ids_list = [f"'{entity['id']}'" async for entity in entity_result]
    entity_ids = ",\n    ".join(entity_ids_list)
    return entity_ids


async def get_search_markdown_format_top_entities_by_entity_result(entity_result:list[Entity])->str:
    entity_list = []
    async for result in entity_result:
        entity = Entity(
            id=result["id"],
            name=result["name"],
            description=result["description"],
            type=result["type"],
            human_readable_id=result["human_readable_id"])
        entity_list.append(entity)

    # create header and separator
    header = "| ID | Name | Description | Type | Human Readable ID |\n"
    separator = "|---|---|---|---|---|\n"

    rows = ""
    for entity in entity_list:
        row = f"| {entity.id} | {entity.name} | {entity.description} | {entity.type} | {entity.human_readable_id} |\n"
        rows += row

    # combie all parts
    entity_markdown_table = "\nEntities:\n" + header + separator + rows
    return entity_markdown_table

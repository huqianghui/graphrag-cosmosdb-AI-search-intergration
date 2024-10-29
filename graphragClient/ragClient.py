
from aiSearch.azureAISearchClient import (
    get_search_markdown_format_top_entities_by_entity_result,
    get_search_top_entities_by_text,
    get_search_top_entity_ids_by_entity_result,
)
from cosmosdb.grelinTool import (
    build_context_data_by_entity_ids,
    get_cosmosDB_community_data_by_level,
)


async def build_context_data(query_text:str,textUnitCount:int=3,entity_relaiton:int=10,communityCount:int=3)->str:
    entityList = await get_search_top_entities_by_text(query_text)
    entity_ids = await get_search_top_entity_ids_by_entity_result(entityList)
    context_without_entity_result =  await build_context_data_by_entity_ids(entity_ids,textUnitCount,entity_relaiton,communityCount)
    entity_markdown_table = await get_search_markdown_format_top_entities_by_entity_result(entityList)
    context_data = context_without_entity_result + entity_markdown_table
    return context_data

async def get_community_data_by_level(level:int)->str:
    return await get_cosmosDB_community_data_by_level(level)
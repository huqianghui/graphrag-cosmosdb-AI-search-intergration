from .grelinClient import get_client
from .grelinQuery import (
    cosmosDB_community_data_by_level_grelin_query_template,
    cosmosDB_community_grelin_query_template,
    cosmosDB_inside_relation_grelin_query_template,
    cosmosDB_outside_relation_grelin_query_template,
    cosmosDB_text_mapping_grelin_query_template,
)


async def get_cosmosDB_text_mapping_grelin_query_result(cosmosDB_text_mapping_grelin_query_result)->str:
    
    # cosmosDB_text_mapping_grelin_query = cosmosDB_text_mapping_grelin_query_template.format(entity_ids=entity_ids, chunk=chunk)
    # cosmosDB_text_mapping_grelin_query_result = await run_gremlin_query(cosmosDB_text_mapping_grelin_query)

    cosmosDB_text_mapping_grelin_query_result_str = "Chunks: \n"
    for idx, record in enumerate(cosmosDB_text_mapping_grelin_query_result):
        for key, value in enumerate(record.keys()):
        # split chunk
            separator = f"\n#########chunk {key + 1:02d} ###########\n"
            record_str = value + "\n\n" 
            cosmosDB_text_mapping_grelin_query_result_str += separator + record_str
    
    return cosmosDB_text_mapping_grelin_query_result_str

async def get_cosmosDB_community_grelin_query_result(cosmosDB_community_grelin_query_result)->str:    
    # split community
    cosmosDB_community_grelin_query_result_str = "\nReports:\n"

    for _, record in enumerate(cosmosDB_community_grelin_query_result):
        record_str = record + "|" 
        cosmosDB_community_grelin_query_result_str += record_str

    return cosmosDB_community_grelin_query_result_str

async def get_cosmosDB_relation_grelin_query_result(cosmosDB_outside_relation_grelin_query_result, cosmosDB_inside_relation_grelin_query_result)->str:
        
        cosmosDB_relation_grelin_query_result = "\nRelationships:"

        for _, record in enumerate(cosmosDB_outside_relation_grelin_query_result):
            record_str = record + "|" 
            cosmosDB_relation_grelin_query_result += record_str

        for _, record in enumerate(cosmosDB_inside_relation_grelin_query_result):
            record_str = record + "|" 
            cosmosDB_relation_grelin_query_result += record_str

        return cosmosDB_relation_grelin_query_result

async def build_context_data_by_entity_ids(entity_ids:str,textUnitCount:int=3,entity_relaiton:int=10,communityCount:int=3)->str:
    client = get_client()
    cosmosDB_text_mapping_grelin_query = cosmosDB_text_mapping_grelin_query_template.format(entity_ids=entity_ids, chunk=textUnitCount)
    cosmosDB_community_grelin_query = cosmosDB_community_grelin_query_template.format(entity_ids=entity_ids, community=communityCount)
    cosmosDB_outside_relation_grelin_query = cosmosDB_outside_relation_grelin_query_template.format(entity_ids=entity_ids, relation=entity_relaiton)
    cosmosDB_inside_relation_grelin_query = cosmosDB_inside_relation_grelin_query_template.format(entity_ids=entity_ids, relation=entity_relaiton)
    
    cosmosDB_text_mapping_result = await get_cosmosDB_text_mapping_grelin_query_result(client.submit(cosmosDB_text_mapping_grelin_query).all().result())
    cosmosDB_community_result = await get_cosmosDB_community_grelin_query_result(client.submit(cosmosDB_community_grelin_query).all().result())
    cosmosDB_entity_relation_result = await get_cosmosDB_relation_grelin_query_result(client.submit(cosmosDB_outside_relation_grelin_query).all().result(),client.submit(cosmosDB_inside_relation_grelin_query).all().result())
    return cosmosDB_text_mapping_result + cosmosDB_community_result + cosmosDB_entity_relation_result

async def  get_cosmosDB_community_data_by_level(level:int)->str:
    client = get_client()
    cosmosDB_community_grelin_query = cosmosDB_community_data_by_level_grelin_query_template.format(level=level)
    cosmosDB_community_data_result = client.submit(cosmosDB_community_grelin_query).all().result()
    return cosmosDB_community_data_result   
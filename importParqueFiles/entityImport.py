import concurrent.futures

import nest_asyncio
import numpy as np

nest_asyncio.apply()

import json
import time

import numpy as np
import pandas as pd

from aiSearch.azureAISearchData import upload_entities_to_index
from appConfig import GRAPHRAG_FOLDER
from cosmosdb.grelinClient import get_client

from .importParqueGremlinQuery import (
    entity_import_gremlin_query,
    entity_text_unit_relation_gremin_query,
)


async def batched_entity_import_gremlin(df, batch_size=100):
    cosmosGremlinClient = get_client()
    total = len(df)
    start_s = time.time()
    for start in range(0, total, batch_size):
        batch = df.iloc[start:min(start+batch_size, total)]
        futureList = []
        for _, row in batch.iterrows():
            entity_params = {
                'id': row['id'],
                'vertex_id': row['vertex_id'],
                'name': row['name'],
                'type': row['type'],
                'description': row['description'],
                'human_readable_id': row['human_readable_id'],
                'text_unit_ids': row['text_unit_ids']
            }
            
            print(f">>Processing entity params: {entity_params}")
            # Create or update the enitity vertex
            try:
                future = cosmosGremlinClient.submit_async(entity_import_gremlin_query, entity_params)
                futureList.append(future)
            except Exception as e:
                print(f"entity creation/update failed: {str(e)}")
                continue

        if futureList :
            done, undone = concurrent.futures.wait(futureList, return_when=concurrent.futures.ALL_COMPLETED)
            print(f"Number of imported entity: {len(done)}")
            print(f"Number of not imported entity : {len(undone)}")
        
        for future in undone:
            print(f"\nFuture in not_done: {future}")
            print(f"  Cancelled: {future.cancelled()}")
            print(f"  Done: {future.done()}")
            print(f"  Exception: {future.exception()}")   
        
    print(f'{total} rows processed in {time.time() - start_s} s.')
    return total


async def entity_text_unit_relation_import_gremlin(df, batch_size=100):
    cosmosGremlinClient = get_client()
    total = len(df)
    start_s = time.time()
    for start in range(0, total, batch_size):
        batch = df.iloc[start:min(start+batch_size, total)]
        futureList = []
        for _, row in batch.iterrows():
            # Create entity text unit vertices and PART_OF edges
            for text_unit_id in row['text_unit_ids']:
                text_unit_params = {
                    'entity_id': row['id'],
                    'text_unit_id': text_unit_id
                }
                print(f"》》Creating text unit relationship: {text_unit_params}")
                try:
                    future = cosmosGremlinClient.submit_async(entity_text_unit_relation_gremin_query, text_unit_params)
                    futureList.append(future)
                except Exception as e:
                    print(f"Text unit relationship creation failed: {str(e)}")

        if futureList :
            done, undone = concurrent.futures.wait(futureList, return_when=concurrent.futures.ALL_COMPLETED)
            print(f"Number of entity and unit file  relation: {len(done)}")
            print(f"Number of entity and unit file  relation: {len(undone)}")
        
        for future in undone:
            print(f"\nFuture in not_done: {future}")
            print(f"  Cancelled: {future.cancelled()}")
            print(f"  Done: {future.done()}")
            print(f"  Exception: {future.exception()}")   
        
    print(f'{total} entity and unit file  relation rows processed in {time.time() - start_s} s.')
    return total
    
async def import_entity_parquet():
    # first，import entity data to AI search
    await import_entity_parquet_AI_search()

    # second, import entity data to cosmos db
    entity_df = pd.read_parquet(f'{GRAPHRAG_FOLDER}/create_final_entities.parquet',
                            columns=["name","type","description","human_readable_id","id","text_unit_ids"])
    entity_df['vertex_id'] = entity_df['id']
    entity_df['text_unit_ids'] = entity_df['text_unit_ids'].apply(  
        lambda x: x.tolist() if isinstance(x, np.ndarray)  
        else x if isinstance(x, list)  
        else [x] if pd.notnull(x)  
        else []  
    )

    total =  await batched_entity_import_gremlin(entity_df)
    await entity_text_unit_relation_import_gremlin(entity_df)
    return total

async def import_entity_parquet_AI_search():
    entity_df = pd.read_parquet(f'{GRAPHRAG_FOLDER}/create_final_entities.parquet',
                            columns=["id","name","type","description","human_readable_id","description_embedding"])
    entity_df['id'] = entity_df['id'].astype(str)
    entity_df['human_readable_id']=entity_df['human_readable_id'].astype(str)
    entity_df['description_embedding'] = entity_df['description_embedding'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
    entity_dicts =  entity_df.to_dict(orient='records')

    upload_entities_to_index(entity_dicts)

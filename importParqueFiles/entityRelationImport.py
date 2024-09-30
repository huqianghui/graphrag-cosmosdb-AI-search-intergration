import concurrent.futures
import json
import time

import nest_asyncio
import numpy as np
import pandas as pd

from cosmosdb.grelinClient import get_client

from .importConfig import GRAPHRAG_FOLDER
from .importParqueGremlinQuery import entity_realtion_import_grelin_query


async def check_vertex_exists(cosmosGremlinClient,vertex_name):
    query = "g.V().has('__Entity__', 'name', name).count()"
    params = {'name': vertex_name}
    try:
        result =  cosmosGremlinClient.submit(query, params).all().result()
        return result[0] > 0  # returns True if vertex exists
    except Exception as e:
        print(f"Vertex existence check failed: {str(e)}")
        return False

async def batched_relation_import_gremlin(df, batch_size=100):
    cosmosGremlinClient = get_client()
    total = len(df)
    start_s = time.time()
    for start in range(0, total, batch_size):
        batch = df.iloc[start:min(start+batch_size, total)]
        futureList = []
        for _, row in batch.iterrows():

            source = row['source'].replace('"', '')
            target = row['target'].replace('"', '')

            #TODO performance Check if both source and target vertices exist
            # if not (await check_vertex_exists(cosmosGremlinClient,source)):
            #     print(f"Source vertex not found: {source}")
            #     continue
            # if not (await check_vertex_exists(cosmosGremlinClient,target)):
            #     print(f"Target vertex not found: {target}")
            #     continue

            rel_params = {
                'id': row['id'],
                'source': source,
                'target': target,
                'rank': row['rank'],
                'weight': row['weight'],
                'human_readable_id': row['human_readable_id'],
                'description': row['description'],
                'text_unit_ids': row['text_unit_ids']
            }
            print(f"Creating/Updating relation: {rel_params}")
            # Create or update the Chunk vertex
            try:
                future = cosmosGremlinClient.submit_async(entity_realtion_import_grelin_query, rel_params)
                futureList.append(future)
            except Exception as e:
                print(f"relation creation/update failed: {str(e)}")
                continue

        if futureList :
            done, undone = concurrent.futures.wait(futureList, return_when=concurrent.futures.ALL_COMPLETED)
            print(f"Number of entity relation: {len(done)}")
            print(f"Number of not imported entity relation: {len(undone)}")
        
        for future in undone:
            print(f"\nFuture in not_done: {future}")
            print(f"  Cancelled: {future.cancelled()}")
            print(f"  Done: {future.done()}")
            print(f"  Exception: {future.exception()}")   

        
    print(f'{total} entity relation rows processed in {time.time() - start_s} s.')
    return total


async def import_entity_relation_parquet():
    rel_df = pd.read_parquet(f'{GRAPHRAG_FOLDER}/create_final_relationships.parquet',
                            columns=["source","target","id","rank","weight","human_readable_id","description","text_unit_ids"])
    rel_df['text_unit_ids'] = rel_df['text_unit_ids'].apply(  
        lambda x: json.dumps(x.tolist()) if isinstance(x, np.ndarray)  
        else json.dumps(x) if isinstance(x, list)  
        else json.dumps([x]) if pd.notnull(x)  
        else json.dumps([])  
    ) 
    return await batched_relation_import_gremlin(rel_df)
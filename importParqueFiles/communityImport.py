import concurrent.futures
import json
import time

import numpy as np
import pandas as pd

from cosmosdb.grelinClient import get_client

from .importConfig import GRAPHRAG_FOLDER
from .importParqueGremlinQuery import (
    community_import_grelin_query,
    entity_community_rel_grelin_query,
)


async def batched_community_import_gremlin(df, batch_size=100):
    cosmosGremlinClient = get_client()
    total = len(df)
    start_s = time.time()
    for start in range(0, total, batch_size):
        futureList = []
        batch = df.iloc[start:min(start+batch_size, total)]
        for _, row in batch.iterrows():
            community_params = {
                'id': row['id'],
                'vertex_id': row['vertex_id'],
                'level': row['level'],
                'title': row['title'],
                'relationship_ids': row['relationship_ids']
            }
            
            print(f">>Processing community params: {community_params}")
            # Create or update the communit vertex
            try:
                future = cosmosGremlinClient.submitAsync(community_import_grelin_query, community_params)
                futureList.append(future)
            except Exception as e:
                print(f"community creation/update failed: {str(e)}")
                continue

        if futureList :
            done, undone = concurrent.futures.wait(futureList, return_when=concurrent.futures.ALL_COMPLETED)
            print(f"Number of community : {len(done)}")
            print(f"Number of not imported community : {len(undone)}")
        
        for future in undone:
            print(f"\nFuture in not_done: {future}")
            print(f"  Cancelled: {future.cancelled()}")
            print(f"  Done: {future.done()}")
            print(f"  Exception: {future.exception()}")       
    
    print(f'{total} community rows processed in {time.time() - start_s} s.')
    return total


async def batched_community_entity_relation_import_gremlin(df, batch_size=100):
    cosmosGremlinClient = get_client()
    total = len(df)
    start_s = time.time()
    for start in range(0, total, batch_size):
        futureList = []
        batch = df.iloc[start:min(start+batch_size, total)]
        for _, row in batch.iterrows():
            # Create communit relation relationship
            for relationship_id in row['relationship_ids']:
                relationship_params = {
                    'community_id': row['id'],
                    'relationship_id': relationship_id
                }
                print(f"》》Creating entity relationship included in community : {relationship_params}")
                try:
                    future = cosmosGremlinClient.submitAsync(entity_community_rel_grelin_query, relationship_params)
                    futureList.append(future)
                except Exception as e:
                    print(f"entity community relationship creation failed: {str(e)}")
        
        if futureList :
            done, undone = concurrent.futures.wait(futureList, return_when=concurrent.futures.ALL_COMPLETED)
            print(f"Number of community entity relation : {len(done)}")
            print(f"Number of not imported community entity relation: {len(undone)}")
        
        for future in undone:
            print(f"\nFuture in not_done: {future}")
            print(f"  Cancelled: {future.cancelled()}")
            print(f"  Done: {future.done()}")
            print(f"  Exception: {future.exception()}")     

    print(f'{total} community entity relation rows processed in {time.time() - start_s} s.')
    return total

async def import_community_parquet():
    community_df = pd.read_parquet(f'{GRAPHRAG_FOLDER}/create_final_communities.parquet', 
                     columns=["id","level","title","text_unit_ids","relationship_ids"])
    community_df['vertex_id'] = community_df['id']
    community_df['relationship_ids'] = community_df['relationship_ids'].apply(  
        lambda x: x.tolist() if isinstance(x, np.ndarray)  
        else x if isinstance(x, list)  
        else [x] if pd.notnull(x)  
        else []  
    )
     
    total =  await batched_community_import_gremlin(community_df)
    await batched_community_entity_relation_import_gremlin(community_df)
    return total
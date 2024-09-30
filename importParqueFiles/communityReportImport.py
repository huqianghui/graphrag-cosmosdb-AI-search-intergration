
import concurrent.futures
import json
import time

import nest_asyncio
import numpy as np
import pandas as pd

from cosmosdb.grelinClient import get_client

from .communityWeightUpdate import update_community_weight_by_entity_count
from .importConfig import GRAPHRAG_FOLDER
from .importParqueGremlinQuery import (
    community_finding_import_grelin_query,
    community_having_finding_grelin_query,
    community_report_merge_grelin_query,
)


async def batched_community_report_import_gremlin(df, batch_size=100):
    client = get_client()
    total = len(df)
    start_s = time.time()
    for start in range(0, total, batch_size):
        futureList = []
        batch = df.iloc[start:min(start+batch_size, total)]
        for _, row in batch.iterrows():
            community_params = {
                'id': row['community'],
                'vertex_id': row['vertex_id'],
                'level': row['level'],
                'title': row['title'],
                'rank': row['rank'],
                'rank_explanation': row['rank_explanation'],
                'full_content': row['full_content'],
                'summary': row['summary']
            }
            print(f"community(report) params: {community_params}")
            # Create or update the Chunk vertex
            try:
                future = client.submit_async(community_report_merge_grelin_query,community_params)
                futureList.append(future)
            except Exception as e:
                print(f"community(report) creation/update failed: {str(e)}")
                continue
        
        if futureList :
            done, undone = concurrent.futures.wait(futureList, return_when=concurrent.futures.ALL_COMPLETED)
            print(f"Number of community report : {len(done)}")
            print(f"Number of not imported community report : {len(undone)}")
        
        for future in undone:
            print(f"\nFuture in not_done: {future}")
            print(f"  Cancelled: {future.cancelled()}")
            print(f"  Done: {future.done()}")
            print(f"  Exception: {future.exception()}")  
    
    print(f'{total} rows of community report processed in {time.time() - start_s} s.')
    return total


async def batched_community_report_finding_import_gremlin(df, batch_size=100):
    client = get_client()
    total = len(df)
    start_s = time.time()
    for start in range(0, total, batch_size):
        futureList = []
        batch = df.iloc[start:min(start+batch_size, total)]
        for _, row in batch.iterrows():
            # Create Document vertices and PART_OF edges
            for finding_idx, finding in enumerate(row['findings']):
                id:str = str(row['community']) + "_" + str(finding_idx)
                finding_params = {
                    'id': id,
                    'communityId': row['community'],
                    'explanation': finding['explanation'],
                    "summary": finding['summary'],
                }
                print(f"》》Creating finding: {finding_params}")            
                try:
                    community_finding_future = client.submit_async(community_finding_import_grelin_query, finding_params)
                    have_finding_result_future = client.submit_async(community_having_finding_grelin_query, finding_params)
                    futureList.append(community_finding_future)
                    futureList.append(have_finding_result_future)
                except Exception as e:
                    print(f"community finding creation failed: {str(e)}")
            
            if futureList :
                done, undone = concurrent.futures.wait(futureList, return_when=concurrent.futures.ALL_COMPLETED)
                print(f"Number of community report finding : {len(done)}")
                print(f"Number of not imported community finding : {len(undone)}")
        
            for future in undone:
                print(f"\nFuture in not_done: {future}")
                print(f"  Cancelled: {future.cancelled()}")
                print(f"  Done: {future.done()}")
                print(f"  Exception: {future.exception()}")  
    
    print(f'{total} rows of community report finding processed in {time.time() - start_s} s.')
    return total

async def import_community_report_parquet():
    community_report_df = pd.read_parquet(f'{GRAPHRAG_FOLDER}/create_final_community_reports.parquet',
                               columns=["id","community","level","title","summary", "findings","rank","rank_explanation","full_content"])

    community_report_df['vertex_id'] = community_report_df['community']
    community_report_df['findings'] = community_report_df['findings'].apply(  
        lambda x: x.tolist() if isinstance(x, np.ndarray)  
        else x if isinstance(x, list)  
        else [x] if pd.notnull(x)  
        else []  
    )
     
    total =  await batched_community_report_import_gremlin(community_report_df)
    await batched_community_report_finding_import_gremlin(community_report_df)
    await update_community_weight_by_entity_count()
    return total

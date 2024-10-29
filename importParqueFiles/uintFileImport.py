import concurrent.futures
import json
import time

import numpy as np
import pandas as pd

from appConfig import GRAPHRAG_FOLDER
from cosmosdb.grelinClient import get_client, run_gremlin_query_with_context

from .importParqueGremlinQuery import (
    chunk_doc_relation_gremlin_query,
    chunk_import_gremlin_query,
)

text_df = pd.read_parquet(f'{GRAPHRAG_FOLDER}/create_final_text_units.parquet',
                          columns=["id","text","n_tokens","document_ids"])
text_df['vertex_id'] = text_df['id']
text_df['document_ids'] = text_df['document_ids'].apply(  
    lambda x: x.tolist() if isinstance(x, np.ndarray)  
    else x if isinstance(x, list)  
    else [x] if pd.notnull(x)  
    else []  
)

async def batched_uint_file_import_gremlin(df, batch_size=100):
    client = get_client()
    total = len(df)
    start_s = time.time()
    for start in range(0, total, batch_size):
        futureList = []
        batch = df.iloc[start:min(start+batch_size, total)]
        for _, row in batch.iterrows():
            chunk_params = {
                'id': row['id'],
                'vertex_id': row['vertex_id'],
                'text': row['text'],
                'n_tokens': int(row['n_tokens'])
            }
            print(f"》》Creating text unit : {chunk_params}")
            # Create or update the Chunk vertex
            try:
                task = client.submit_async(chunk_import_gremlin_query, chunk_params)
                futureList.append(task)
            except Exception as e:
                print(f"Chunk creation/update failed: {str(e)}")
                continue

        if futureList :
            done, undone = concurrent.futures.wait(futureList, return_when=concurrent.futures.ALL_COMPLETED)
            print(f"Number of imported unit file entity: {len(done)}")
            print(f"Number of not imported unit file entity: {len(undone)}")
        
        for future in undone:
            print(f"\nFuture in not_done: {future}")
            print(f"  Cancelled: {future.cancelled()}")
            print(f"  Done: {future.done()}")
            print(f"  Exception: {future.exception()}")


    print(f'{total} uint_file rows processed in {time.time() - start_s} s.')
    return total

async def batched_uint_file_doc_relation_process(df, batch_size=50):
    client = get_client()
    total = len(df)
    start_s = time.time()
    for start in range(0, total, batch_size):
        futureList = []
        batch = df.iloc[start:min(start+batch_size, total)]
        for _, row in batch.iterrows():
            # Create Document vertices and PART_OF edges
            for doc_id in row['document_ids']:
                doc_params = {
                    'chunk_id': row['id'],
                    'doc_id': doc_id
                }
                print(f"》》Creating Document relationship: {doc_params}")
                try:
                    future = client.submit_async(chunk_doc_relation_gremlin_query, doc_params)
                    futureList.append(future)
                except Exception as e:
                    print(f"Document relationship creation failed: {str(e)}")
        
        if futureList :
            done, undone = concurrent.futures.wait(futureList, return_when=concurrent.futures.ALL_COMPLETED)
            print(f"Number of imported unit file document relation: {len(done)}")
            print(f"Number of not imported unit file document relation: {len(undone)}")
        
        for future in undone:
            print(f"\nFuture in not_done: {future}")
            print(f"  Cancelled: {future.cancelled()}")
            print(f"  Done: {future.done()}")
            print(f"  Exception: {future.exception()}")

    print(f'{total} uint_file_doc_relation rows processed in {time.time() - start_s} s.')
    return total

async def import_unit_file_parquet():
    text_df = pd.read_parquet(f'{GRAPHRAG_FOLDER}/create_final_text_units.parquet',
                          columns=["id","text","n_tokens","document_ids"])
    text_df['vertex_id'] = text_df['id']
    text_df['document_ids'] = text_df['document_ids'].apply(  
        lambda x: x.tolist() if isinstance(x, np.ndarray)  
        else x if isinstance(x, list)  
        else [x] if pd.notnull(x)  
        else []
    )  
    total = await batched_uint_file_import_gremlin(text_df)
    await batched_uint_file_doc_relation_process(text_df)
    return total
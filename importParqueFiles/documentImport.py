import asyncio
import concurrent.futures
import json
import time

import numpy as np
import pandas as pd

from cosmosdb.grelinClient import get_client

from .importConfig import GRAPHRAG_FOLDER
from .importParqueGremlinQuery import doc_import_gremlin_query


async def batched_doc_import_gremlin(df, batch_size=100):
    client = get_client()
    total = len(df)
    start_s = time.time()
    for start in range(0, total, batch_size):
        futureList = []
        batch = df.iloc[start:min(start+batch_size, total)]
        for _, row in batch.iterrows():
            params = {
                'id': row['id'],
                'vertex_id': row['vertex_id'],
                'title': row['title'],
                'raw_content': row['raw_content'],
                'text_unit_ids': row['text_unit_ids']
            }
            print(f">>Processing doc params: {row['title']}")
            try:  
                task = client.submit_async(doc_import_gremlin_query, params)
                futureList.append(task)
            except Exception as e:  
                print(f"Query failed: {str(e)}")
        
        if futureList:
            done, undone = concurrent.futures.wait(futureList, return_when=concurrent.futures.ALL_COMPLETED)
            print(f"Number of imported unit file document relation: {len(done)}")
            print(f"Number of not imported unit file document relation: {len(undone)}")
        
        for future in undone:
            print(f"\nFuture in not_done: {future}")
            print(f"  Cancelled: {future.cancelled()}")
            print(f"  Done: {future.done()}")
            print(f"  Exception: {future.exception()}")


    print(f'{total} document rows in {time.time() - start_s} s.')
    return total

async def import_document_parquet():
    doc_df = pd.read_parquet(f'{GRAPHRAG_FOLDER}/create_final_documents.parquet', columns=["id", "title","raw_content","text_unit_ids"])
    doc_df['vertex_id'] = doc_df['id']
    doc_df['text_unit_ids'] = doc_df['text_unit_ids'].apply(  
        lambda x: json.dumps(x.tolist()) if isinstance(x, np.ndarray)  
        else json.dumps(x) if isinstance(x, list)  
        else json.dumps([x]) if pd.notnull(x)  
        else json.dumps([])  
    )  
    return await batched_doc_import_gremlin(doc_df)

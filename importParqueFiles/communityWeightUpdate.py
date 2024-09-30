
import concurrent.futures
import json
import time

import nest_asyncio
import numpy as np
import pandas as pd

from cosmosdb.grelinClient import get_client

from .importParqueGremlinQuery import (
    community_entity_count_grelin_query,
    community_weight_update_query,
)


# Gremlin query
async def update_community_weight_by_entity_count():
    client = get_client()
    try:
        # Execute the query
        community_enity_count_results = client.submit(community_entity_count_grelin_query).all().result()
        print(f"community_enity_count_results:{community_enity_count_results}")

        futureList=[]
        # update weight
        for  community_enity_count_result in community_enity_count_results:
            for community_id, entity_count in community_enity_count_result.items():
                print(f"update weight: Community ID: {community_id}, Entity Count: {entity_count}")
                future = client.submit_async(community_weight_update_query,{'community_id': community_id, 'chunkCount': entity_count})
                futureList.append(future)
        
        if futureList:
            done, undone = concurrent.futures.wait(futureList, return_when=concurrent.futures.ALL_COMPLETED)
            print(f"Number of community weight updated: {len(done)}")
            print(f"Number of not updated community weight: {len(undone)}")

        for future in undone:
            print(f"\nFuture in not_done: {future}")
            print(f"  Cancelled: {future.cancelled()}")
            print(f"  Done: {future.done()}")
            print(f"  Exception: {future.exception()}")

    except Exception as e:
        print(f"An error occurred: {e}")

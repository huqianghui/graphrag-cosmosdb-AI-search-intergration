
import os

from dotenv import load_dotenv
from gremlin_python.driver import client as gremlin_client
from gremlin_python.driver.serializer import GraphSONSerializersV2d0

load_dotenv()


endpoint = os.getenv("cosmos_endpoint")
key = os.getenv("cosmos_key")

DATABASE_NAME = os.getenv("cosmos_database_name")
GRAPH_NAME = os.getenv("cosmos_database_graph_name")


def get_client():  
    return gremlin_client.Client(  
        endpoint,  
        'g',  
        username=f"/dbs/{DATABASE_NAME}/colls/{GRAPH_NAME}",  
        password=key,  
        message_serializer=GraphSONSerializersV2d0()  
    )  

async def run_gremlin_query(gremlin_query: str):
    import nest_asyncio
    nest_asyncio.apply()
    client = get_client()  
    try:  
        result = client.submit(gremlin_query).all().result()
    finally:  
        client.close()  # Close the client synchronously  
    return result

async def run_gremlin_query_with_context(gremlin_query: str,context):
    import nest_asyncio
    nest_asyncio.apply()
    client = get_client()  
    try:  
        result =  client.submit(gremlin_query,bindings=context).all().result()
    finally:  
        client.close()  # Close the client synchronously  
    return result    
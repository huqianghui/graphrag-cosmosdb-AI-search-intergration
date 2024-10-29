from cosmosdb.grelinClient import run_gremlin_query
from cosmosdb.grelinQuery import cosmosDB_max_community_level_grelin_query

# init max level of community
max_level = None

async def get_max_level_by_startup_event():
    global max_level
    try:
        # query max level of community
        result = await run_gremlin_query(cosmosDB_max_community_level_grelin_query)
        
        # check the result
        if result and len(result) > 0 :
            max_level = int(result[0])
        else:
            max_level = None  # if no result,then None
            
        return max_level
    except Exception as e:
        # if there is some exeception,then set max_level  None
        print(f"Error fetching max level: {e}")
        max_level = None

async def get_max_level():
    global max_level
    if max_level is None:
        max_level =  await get_max_level_by_startup_event()
        if max_level is None:
            raise ValueError("The community of max level is not found. Please check the cosmosdb.")
    return max_level
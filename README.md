# graphrag-cosmosdb-AI-search-intergration

step1) 

config .env file from .env_template and importParqueFiles/importConfig.py
### import entity to azure AI search

![entity_import2_ai_search](./images/entity_import2_ai_search.png)


### import all entity and relation to azure cosmosDB gremlin database graph

![entity_import2_cosmosdb](./images/entity_import2_cosmosdb.png)

### search entity from AI search and build context from cosmosdb,then give the LLM response

![graphrag_query_cosmosdb](./images/graphrag_query_cosmosdb.png)

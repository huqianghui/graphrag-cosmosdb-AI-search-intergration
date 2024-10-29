# graphrag-cosmosdb-AI-search-intergration

**steps**：

a） generate parque files by graphrag

b)   copy .env_template to .env and config the env variables.

c)   copy  .appConfig.py_template to .appConfig.py, and config variables.

d)   start the app by run python app.py 

e) call the get api: v1/import to import parque files into  AI search and cosmosDB

then you can call api: /v1/localSearch to get graphrag local search with AI search and cosmosDB, and /v1/globalSearch to get global search with AI search and cosmosDB


main step screenshot 

1. import entity to azure AI search

![entity_import2_ai_search](./images/entity_import2_ai_search.png)

2. import all entity and relation to azure cosmosDB gremlin database graph

![entity_import2_cosmosdb](./images/entity_import2_cosmosdb.png)

3. search entity from AI search and build context from cosmosdb,then give the LLM response

![graphrag_query_cosmosdb](./images/graphrag_query_cosmosdb.png)

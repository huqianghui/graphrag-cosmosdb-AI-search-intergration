# graphrag-cosmosdb-AI-search-intergration

**steps**：

a） generate parque files by graphrag(refer: https://microsoft.github.io/graphrag/get_started/)
<img width="787" alt="Screenshot 2024-11-12 at 9 57 06 AM" src="https://github.com/user-attachments/assets/c9feb39f-bb23-4b35-b8af-aa5c30a4151c">


b)   copy .env_template to .env and config the env variables.

c)   copy  .appConfig.py_template to .appConfig.py, and config variables.

d)   start the app by run python app.py 

e) call the get api: v1/import to import parque files into  AI search and cosmosDB

then you can call api: /v1/localSearch to get graphrag local search with AI search and cosmosDB, and /v1/globalSearch to get global search with AI search and cosmosDB


main step screenshot 

1. import entity to azure AI search

![entity_import2_ai_search](./images/entity_import2_ai_search.png)

2. import all entity and relation to azure cosmosDB gremlin database graph(cosmosDB's Partition key: vertex_id)
<img width="1442" alt="Screenshot 2024-11-12 at 8 57 23 AM" src="https://github.com/user-attachments/assets/f7bc4af8-4310-4c47-9e4a-16836bde42ad">


![entity_import2_cosmosdb](./images/entity_import2_cosmosdb.png)

3. search entity from AI search and build context from cosmosdb,then give the LLM response

![graphrag_query_cosmosdb](./images/graphrag_query_cosmosdb.png)

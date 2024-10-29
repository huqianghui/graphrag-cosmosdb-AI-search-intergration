import asyncio

from tqdm import tqdm

from appConfig import response_type
from azureOpenAI.azureOpenAIClient import (
    get_azureOpenAI_async_client,
    llm_deployment_name,
)
from azureOpenAI.globalSearchMapPrompt import process_map_process
from azureOpenAI.localSearchPrompt import LOCAL_SEARCH_SYSTEM_PROMPT
from graphragClient.ragClient import build_context_data, get_community_data_by_level

from .globalSearchReducePrompt import reduce_chain


async def get_graphrag_response_by_text(query_text)->str:
    context_data = await build_context_data(query_text)
    LOCAL_SEARCH_SYSTEM_PROMPT_WITH_DATA = LOCAL_SEARCH_SYSTEM_PROMPT.format(response_type=response_type, context_data=context_data)

    messages = [
    {"role": "system", "content": LOCAL_SEARCH_SYSTEM_PROMPT_WITH_DATA},
    {"role": "user", "content": query_text}]

    azureOpenAI = get_azureOpenAI_async_client()
    response = await azureOpenAI.chat.completions.create(
        model=llm_deployment_name,
        messages=messages)
    
    return response.choices[0].message.content




async def global_retriever(query: str, level: int) -> str:
    community_data = await get_community_data_by_level(level)
    intermediate_results = []

    tasks = [process_map_process(query, community) for community in community_data]
    intermediate_results = await asyncio.gather(*tasks)

    final_response = await reduce_chain.ainvoke(
        {
            "report_data": intermediate_results,
            "question": query,
            "response_type": response_type,
        }
    )
    return final_response
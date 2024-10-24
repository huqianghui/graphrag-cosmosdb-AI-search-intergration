import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from appConfig import PORT, response_type
from azureOpenAI.azureOpenAIClient import (
    get_azureOpenAI_async_client,
    llm_deployment_name,
)
from azureOpenAI.localSearchPrompt import LOCAL_SEARCH_SYSTEM_PROMPT
from graphragClient.ragClient import build_context_data
from httpModel.requestModel import ChatCompletionRequest
from importParqueFiles.importGraphragFile import import_parquet_files

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()


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


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    logger.info(f"Received request: {request}")
    prompt = request.messages[-1].content
    response = await get_graphrag_response_by_text(prompt)

    return JSONResponse(content={"message": response})


@app.get("/v1/import")
async def import():
    response = await import_parquet_files()
    return JSONResponse(content={"message": response})


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

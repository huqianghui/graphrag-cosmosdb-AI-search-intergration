import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from appConfig import PORT
from appinitialization.appInitializer import (
    get_max_level,
    get_max_level_by_startup_event,
)
from azureOpenAI.graphragAzureOpenAIQuery import (
    get_graphrag_response_by_text,
    global_retriever,
)
from httpModel.requestModel import ChatCompletionRequest
from importParqueFiles.importGraphragFile import import_parquet_files

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import os

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


app = FastAPI()

@app.post("/v1/localSearch")
async def local_search(request: ChatCompletionRequest):
    logger.info(f"Received request: {request}")
    prompt = request.messages[-1].content
    response = await get_graphrag_response_by_text(prompt)

    return JSONResponse(content={"message": response})

@app.post("/v1/globalSearch")
async def global_search(request: ChatCompletionRequest):
    logger.info(f"Received request: {request}")
    max_level = await get_max_level()
    prompt = request.messages[-1].content   
    if(max_level and request.community_level <= max_level):
        response = await global_retriever(prompt,request.community_level)
    elif(max_level and request.community_level > max_level ):
        response = await global_retriever(prompt,max_level)

    return JSONResponse(content={"message": response})

@app.get("/v1/import")
async def parque_files_import():
    response = await import_parquet_files()
    return JSONResponse(content={"message": response})

@app.on_event("startup")
async def startup_event() :
    await get_max_level_by_startup_event()

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

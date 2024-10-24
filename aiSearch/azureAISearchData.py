import argparse
import asyncio
import dataclasses
import os
import time
from datetime import datetime

import pandas as pd
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    AzureOpenAIParameters,
    AzureOpenAIVectorizer,
    CorsOptions,
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from dotenv import load_dotenv
from tqdm import tqdm

from .azureAISearchClient import get_index_client, get_search_client

# 加载 .env 文件
load_dotenv()

index_name = os.getenv("ai_search_index_name")


def create_search_index(index_name, index_client):
    print(f"Ensuring search index {index_name} exists")
    if index_name not in index_client.list_index_names():
        
        index = SearchIndex(
            name=index_name,
            cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=600),
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.String, key=True,searchable=True, filterable=True, sortable=True, facetable=True),
                SearchableField(name="name", type=SearchFieldDataType.String, analyzer_name="zh-Hans.microsoft"),
                SearchableField(name="type", type=SearchFieldDataType.String, analyzer_name="zh-Hans.microsoft"),
                SearchableField(name="description", type=SearchFieldDataType.String, analyzer_name="zh-Hans.microsoft"),
                SimpleField(name="human_readable_id", type=SearchFieldDataType.String,Searchable=True,filterable=True, sortable=True, facetable=True),
                SearchField(name="description_embedding", 
                            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                            hidden=False, 
                            searchable=True, 
                            filterable=False, 
                            sortable=False, 
                            facetable=False,
                            vector_search_dimensions=1536, 
                            vector_search_profile_name="azureOpenAIHnswProfile")
            ],
            semantic_search=SemanticSearch(
                configurations=[
                    SemanticConfiguration(
                        name="default",
                        prioritized_fields=SemanticPrioritizedFields(
                            title_field=SemanticField(field_name="name"),
                            content_fields=[
                                SemanticField(field_name="description")
                            ],
                            keywords_fields=[
                                SemanticField(field_name="type")
                            ]
                        ),
                    )
                ]
            ),
            vector_search=VectorSearch(
                algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
                profiles=[VectorSearchProfile(name="azureOpenAIHnswProfile",algorithm_configuration_name="myHnsw",vectorizer="azureOpenAIVectorizer")],
                vectorizers=[
                    AzureOpenAIVectorizer(
                        name="azureOpenAIVectorizer",
                        azure_open_ai_parameters=AzureOpenAIParameters(
                            resource_uri=os.getenv("aoai_resource_uri"),
                            deployment_id=os.getenv("aoai_embedding_deployment_name"),
                            model_name=os.getenv("aoai_embedding_model_name"),
                            api_key=os.getenv("aozai_api_key")))
                ]
            )
        )
        print(f"Creating {index_name} search index")
        index_client.create_index(index)
    else:
        print(f"Search index {index_name} already exists")

def upload_entities_to_index(entities, upload_batch_size=50):
    
    create_search_index(index_name, get_index_client())
    search_client = get_search_client()

    to_upload_dicts = []

    for entity in entities:
        # add id to documents
        entity.update({"@search.action": "upload", "id": str(entity["id"])})

        if "description_embedding" in entity and entity["description_embedding"] is None:
            del entity["description_embedding"]

        to_upload_dicts.append(entity)

    # Upload the documents in batches of upload_batch_size
    for i in tqdm(
        range(0, len(to_upload_dicts), upload_batch_size), desc="Indexing Chunks..."
    ):
        batch = to_upload_dicts[i : i + upload_batch_size]
        results = search_client.upload_documents(documents=batch)
        num_failures = 0
        errors = set()
        for result in results:
            if not result.succeeded:
                print(
                    f"Indexing Failed for {result.key} with ERROR: {result.error_message}"
                )
                num_failures += 1
                errors.add(result.error_message)
        if num_failures > 0:
            raise Exception(
                f"INDEXING FAILED for {num_failures} documents. Please recreate the index."
                f"To Debug: PLEASE CHECK chunk_size and upload_batch_size. \n Error Messages: {list(errors)}"
            )
        

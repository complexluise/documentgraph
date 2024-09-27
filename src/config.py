import os

from pydantic import BaseModel


class ChunkConfig(BaseModel):
    chunking_strategy: str = "recursive"  # Options: "recursive", "character", "semantic", "tiktoken"
    chunk_size: int = 100
    chunk_overlap: int = 20
    embedding_dimension: int = 1536  # Assuming you're using OpenAI's default embedding size


class ETLConfig(BaseModel):
    n_jobs: int = 4
    chunk_size: int = 1000
    embedding_dimension: int = 768
    graph_db_url: str = os.getenv("")
    llm_api_key: str

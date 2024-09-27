import os

from pydantic import BaseModel


class EmbeddingConfig(BaseModel):
    model_name: str = "text-embedding-3-small"
    embedding_dimension: int = (
        1536  # Assuming you're using OpenAI's default embedding size
    )


class ChunkConfig(BaseModel):
    chunking_strategy: str = (
        "recursive"  # Options: "recursive", "character", "semantic", "tiktoken"
    )
    chunk_size: int = 100
    chunk_overlap: int = 20


class ETLConfig(BaseModel):
    n_jobs: int = 4
    graph_db_url: str = os.getenv("NEO4J_URI")
    llm_api_key: str = os.getenv("OPENAI_API_KEY")
    chunk_config: ChunkConfig
    embedding_config: EmbeddingConfig

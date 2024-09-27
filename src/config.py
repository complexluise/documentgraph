import os

from pydantic import BaseModel


class Neo4JConfig(BaseModel):
    uri: str = os.getenv("NEO4J_URI")
    user: str = os.getenv("NEO4J_USER")
    password: str = os.getenv("NEO4J_PASSWORD")


class EmbeddingConfig(BaseModel):
    emb_model: str = "text-embedding-3-small"
    emb_dimension: int = (
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
    graph_db_config: Neo4JConfig = Neo4JConfig()
    chunk_config: ChunkConfig = ChunkConfig()
    embedding_config: EmbeddingConfig = EmbeddingConfig()

    model_config = {
        "arbitrary_types_allowed": True
    }

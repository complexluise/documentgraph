import os

from pydantic import BaseModel


class Neo4JConfig(BaseModel):
    uri: str = os.getenv("NEO4J_URI")
    user: str = os.getenv("NEO4J_USER")
    password: str = os.getenv("NEO4J_PASSWORD")


class EmbeddingConfig(BaseModel):
    model: str = "text-embedding-3-small"
    dimension: int = 1536  # Assuming you're using OpenAI's default embedding size


class ChunkConfig(BaseModel):
    strategy: str = (
        "recursive"  # Options: "recursive", "character", "semantic", "tiktoken"
    )
    size: int = 2000
    overlap: int = 200


class OpenAIConfig(BaseModel):
    api_key: str = os.getenv("OPENAI_API_KEY")
    model: str = "gpt-4o-mini-2024-07-18"


class ETLConfig(BaseModel):
    n_jobs: int = 4
    graph_db_config: Neo4JConfig = Neo4JConfig()
    chunk_config: ChunkConfig = ChunkConfig()
    llm_config: OpenAIConfig = OpenAIConfig()
    embedding_config: EmbeddingConfig = EmbeddingConfig()
    model_config = {"arbitrary_types_allowed": True}

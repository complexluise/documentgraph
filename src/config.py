from pydantic import BaseModel


class Config(BaseModel):
    n_jobs: int = 4
    chunk_size: int = 1000
    embedding_dimension: int = 768
    graph_db_url: str
    llm_api_key: str

from src.config import ETLConfig


class QueryEngine:
    def __init__(self, config: ETLConfig):
        self.config = config

    def process_query(self, query: str) -> str:
        # Implementación del procesamiento de consultas
        pass

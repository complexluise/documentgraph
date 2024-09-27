from src.config import ETLConfig
from src.models import Entity, Relationship, TextChunk


class KnowledgeGraphLoader:
    def __init__(self, config: ETLConfig):
        self.config = config

    def load_incremental(self, entities: list[Entity], relationships: list[Relationship], chunks: list[TextChunk]) -> None:
        # Implementación de la carga incremental en la base de datos de grafos
        pass

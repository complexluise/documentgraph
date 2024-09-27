from src.config import Config
from src.models import Entity, Relationship, Chunk


class GraphLoader:
    def __init__(self, config: Config):
        self.config = config

    def load_incremental(self, entities: list[Entity], relationships: list[Relationship], chunks: list[Chunk]) -> None:
        # Implementación de la carga incremental en la base de datos de grafos
        pass

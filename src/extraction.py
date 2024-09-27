from src.config import Config


class DataExtractor:
    def __init__(self, config: Config):
        self.config = config

    def extract(self, source: str) -> Document:
        # Implementación de la extracción
        pass
from abc import ABC, abstractmethod

from src.config import ETLConfig
from src.models import Document


class DataExtractor(ABC):
    def __init__(self, config: ETLConfig):
        self.config = config

    @abstractmethod
    def extract(self, source: str) -> Document:
        # Implementación de la extracción
        pass


class DocumentExtractor(DataExtractor):
    def extract(self, source: str) -> Document:
        # Implementación de la extracción de documentos
        pass

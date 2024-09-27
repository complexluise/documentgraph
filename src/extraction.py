import os
from abc import ABC, abstractmethod

from src.config import ETLConfig
from src.models import Document


class DataExtractor(ABC):
    def __init__(self, config: ETLConfig):
        self.config = config

    @abstractmethod
    def extract(self) -> Document:
        pass


class DocumentExtractor(DataExtractor):
    def extract(self) -> Document:
        for filename in os.listdir(self.config.input_folder):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.config.input_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    yield Document(filename=filename, content=content)

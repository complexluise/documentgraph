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
        """
        Extracts documents from the configured input folder and yields them as Document objects.

        This method iterates through the files in the input folder, and for each file with a .txt extension, it reads the file content and yields a Document object with the file's ID, filename, and content.
        """
        for i, filename in enumerate(os.listdir(self.config.input_folder)):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.config.input_folder, filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    yield Document(id=i, filename=filename, content=content)

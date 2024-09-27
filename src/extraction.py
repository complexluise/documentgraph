from abc import ABC, abstractmethod
from pathlib import Path

from src.config import ETLConfig
from src.models import Document


class DataExtractor(ABC):
    def __init__(self, config: ETLConfig):
        self.config = config

    @abstractmethod
    def extract(self, *args, **kwargs) -> Document:
        pass


class DocumentExtractor(DataExtractor):
    def extract(self, input_folder) -> Document:
        """
        Extracts documents from the configured input folder and yields them as Document objects.

        This method iterates through the files in the input folder, and for each file with a .txt extension, it reads the file content and yields a Document object with the file's ID, filename, and content.
        """
        input_path = Path(input_folder)
        for i, file_path in enumerate(input_path.glob("*.txt")):
            with file_path.open("r", encoding="utf-8") as file:
                content = file.read()
                yield Document(id=i, filename=file_path.name, content=content)

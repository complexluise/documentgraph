import logging
from abc import ABC, abstractmethod
from pathlib import Path

from documentgraph.config import ETLConfig
from documentgraph.models import Document


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
        If no files are found, it logs a message and exits the program.
        """

        project_root = Path(__file__).resolve().parent.parent
        input_path = project_root / input_folder
        files = list(input_path.glob("*.txt"))

        if not files:
            import sys

            logging.warning(
                f"No archivos .txt encontrados {input_path}. Salir del programa."
            )
            sys.exit(1)

        for file_path in files:
            with file_path.open("r", encoding="utf-8") as file:
                content = file.read()
                yield Document(filename=file_path.name, content=content)

from typing import Tuple, List
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from src.config import ChunkConfig, ETLConfig
from src.models import Document, TextChunk, Entity, Relationship


class TextProcessor:
    def __init__(self, config: ETLConfig):
        self.config = config

    @staticmethod
    def process(document: Document) -> Document:
        # Implementación del procesamiento de texto
        return document

    def create_chunks(self, document: Document) -> List[TextChunk]:
        text = document.content
        chunks = []

        if self.config.chunking_strategy == "recursive":
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_config.chunk_size,
                chunk_overlap=self.config.chunk_config.chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )
            chunks = text_splitter.create_documents([text])

        elif self.config.chunking_strategy == "character":
            text_splitter = CharacterTextSplitter(
                separator="\n\n",
                chunk_size=self.config.chunk_config.chunk_size,
                chunk_overlap=self.config.chunk_config.chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )
            chunks = text_splitter.create_documents([text])

        elif self.config.chunking_strategy == "semantic":
            text_splitter = SemanticChunker(
                OpenAIEmbeddings(model=self.config.embedding_config.model_name)
            )
            chunks = text_splitter.create_documents([text])

        elif self.config.chunking_strategy == "tiktoken":
            text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
                encoding_name="cl100k_base",
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
            )
            chunks = text_splitter.split_text(text)

        return [
            TextChunk(content=chunk.page_content, metadata=chunk.metadata)
            for chunk in chunks
        ]


class EmbeddingGenerator:
    def __init__(self, config: ETLConfig):
        self.config = config
        self.model = OpenAIEmbeddings(model=self.config.embedding_config.model_name)

    def generate(self, chunk: TextChunk) -> List[float]:
        return self.model.embed_query(chunk.text)


class EntityRelationExtractor:
    def __init__(self, config: ETLConfig):
        self.config = config

    def extract(self, chunk: TextChunk) -> Tuple[list[Entity], list[Relationship]]:
        # Implementación del análisis de entidades y relaciones
        pass

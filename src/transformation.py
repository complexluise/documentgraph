import uuid

from typing import Tuple

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate

from src.config import ETLConfig
from src.models import Document, TextChunk, Entity, Relationship, ExtractionResult


class TextProcessor:
    def __init__(self, config: ETLConfig):
        self.config = config

    @staticmethod
    def process(document: Document) -> Document:
        # Implementación del procesamiento de texto
        return document

    def create_chunks(self, document: Document) -> list[TextChunk]:
        text = document.content
        chunks = []

        if self.config.chunk_config.strategy == "recursive":
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_config.size,
                chunk_overlap=self.config.chunk_config.overlap,
                length_function=len,
                is_separator_regex=False,
            )
            chunks = text_splitter.create_documents([text])

        elif self.config.chunk_config.strategy == "character":
            text_splitter = CharacterTextSplitter(
                separator="\n\n",
                chunk_size=self.config.chunk_config.size,
                chunk_overlap=self.config.chunk_config.overlap,
                length_function=len,
                is_separator_regex=False,
            )
            chunks = text_splitter.create_documents([text])

        elif self.config.chunk_config.strategy == "semantic":
            text_splitter = SemanticChunker(
                OpenAIEmbeddings(model=self.config.embedding_config.emb_model)
            )
            chunks = text_splitter.create_documents([text])

        elif self.config.chunk_config.strategy == "tiktoken":
            text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
                encoding_name="cl100k_base",
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
            )
            chunks = text_splitter.split_text(text)

        return [
            TextChunk(
                content=chunk.page_content,
                metadata=chunk.metadata,
                document_id=document.id,
            )
            for chunk in chunks
        ]


class EmbeddingGenerator:
    def __init__(self, config: ETLConfig):
        self.config = config
        self.model = OpenAIEmbeddings(model=self.config.embedding_config.emb_model)

    def generate(self, chunk: TextChunk) -> list[float]:
        return self.model.embed_query(chunk.text)


class EntityRelationExtractor:
    def __init__(self, config: ETLConfig):
        self.config = config
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k")
        self.parser = PydanticOutputParser(pydantic_object=ExtractionResult)

    def extract(self, chunk: TextChunk) -> Tuple[list[Entity], list[Relationship]]:
        prompt = ChatPromptTemplate.from_template(
            "Extrae las entidades y relaciones del siguiente texto. "
            "Proporciona la salida en formato JSON que cumpla con el siguiente esquema:\n"
            "{format_instructions}\n\n"
            "Texto: {text}"
        )

        chain = prompt | self.llm | self.parser

        result = chain.invoke(
            {
                "format_instructions": self.parser.get_format_instructions(),
                "text": chunk.content,
            }
        )

        # Asignar IDs únicos a las entidades
        for entity in result.entities:
            entity.id = str(uuid.uuid4())

        # Actualizar los IDs de las relaciones
        for relationship in result.relationships:
            source_entity = next(
                (e for e in result.entities if e.name == relationship.source_id), None
            )
            target_entity = next(
                (e for e in result.entities if e.name == relationship.target_id), None
            )
            if source_entity and target_entity:
                relationship.source_id = source_entity.id
                relationship.target_id = target_entity.id

        return result.entities, result.relationships

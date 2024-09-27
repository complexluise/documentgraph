import json
import re
import uuid

from typing import Tuple

from langchain_core.runnables import RunnableLambda
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
                OpenAIEmbeddings(model=self.config.embedding_config.model)
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
        self.model = OpenAIEmbeddings(model=self.config.embedding_config.model)

    def generate(self, chunk: TextChunk) -> list[float]:
        return self.model.embed_query(chunk.content)


class EntityRelationExtractor:
    def __init__(self, config: ETLConfig):
        self.config = config
        self.llm = ChatOpenAI(model_name=config.llm_config.model)
        self.parser = RunnableLambda(
            lambda x: ExtractionResult(
                **json.loads(
                    re.search(
                        r"(?:^|\n)```json\n([\s\S]*?)\n```", x.content, re.DOTALL
                    ).group(1)
                )
            )
        )

    def extract(self, chunk: TextChunk) -> Tuple[list[Entity], list[Relationship]]:
        prompt = ChatPromptTemplate.from_template(
            "Extrae las entidades y relaciones del siguiente texto.\n"
            "Primero razona un poco para identificar cuales son las mismas entidades.\n"
            "Proporciona la salida en formato JSON inline code with ``` que cumpla con el siguiente esquema:\n"
            "{{\n"
            '  "entities": [\n'
            "    {{\n"
            '      "name": "string",\n'
            '      "type": "string",\n'
            '      "properties": {{}}\n'
            "    }}\n"
            "  ],\n"
            '  "relationships": [\n'
            "    {{\n"
            '      "source_name": "string",\n'
            '      "target_name": "string",\n'
            '      "type": "string",\n'
            '      "properties": {{}}\n'
            "    }}\n"
            "  ]\n"
            "}}\n\n"
            "Texto: {text}"
        )

        chain = prompt | self.llm | self.parser

        result: ExtractionResult = chain.invoke({"text": chunk.content})

        # Actualizar los IDs de las relaciones
        updated_relationships = []
        for relationship in result.relationships:
            source_entity = next(
                (e for e in result.entities if e.name == relationship.source_name), None
            )
            target_entity = next(
                (e for e in result.entities if e.name == relationship.target_name), None
            )
            if source_entity and target_entity:
                updated_relationship = relationship.model_copy(
                    update={
                        "source_id": source_entity.id,
                        "target_id": target_entity.id,
                    }
                )
            else:
                updated_relationship = relationship
            updated_relationships.append(updated_relationship)

        return result.entities, updated_relationships

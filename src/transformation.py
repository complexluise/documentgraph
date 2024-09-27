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

    def extract_chain(self):
        prompt = ChatPromptTemplate.from_template(
            """
            You are tasked with extracting entities and relationships from a given text. Here is the text you will analyze:
            
            <text>
            {TEXT}
            </text>
            
            Your goal is to identify entities and their relationships within this text, and then present them in a specific JSON format. Follow these steps:
            
            1. Carefully read and analyze the text.
            
            2. In a <reasoning> section, think through the entities you've identified. Consider which mentions might refer to the same entity and how you can consolidate them.
            
            3. Identify and categorize entities:
               - Look for proper nouns, important concepts, or recurring themes.
               - Determine a suitable type for each entity (e.g., Person, Organization, Location, Concept).
               - Note any relevant properties for each entity.
            
            4. Identify relationships between entities:
               - Look for verbs or phrases that connect entities.
               - Determine the type of relationship (e.g., "works for", "located in", "part of").
               - Note any relevant properties for each relationship.
               - Relationships should have a verbal phrase as an example (nacio) + prepositional phrase (EnCiudad) -> nacioenCiudad
            
            5. After your analysis, provide your output in the following JSON format, enclosed in triple backticks ():
            
            json
            {{
              "entities": [
                {{
                  "name": "Entity Name",
                  "type": "Entity Type",
                  "properties": {{}}
                }}
              ],
              "relationships": [
                {{
                  "source_name": "Source Entity Name",
                  "target_name": "Target Entity Name",
                  "type": "Relationship Type",
                  "properties": {{}}
                }}
              ]
            }}
            ```
            
            Remember:
            - Entity names should be consistent throughout the JSON.
            - Include all relevant entities and relationships you've identified.
            - If there are no properties for an entity or relationship, leave the "properties" object empty.
            - Ensure your JSON is properly formatted and valid.
            
            Begin your analysis now, starting with the <reasoning> section, followed by your JSON output.
            """
        )

        def update_relationships(result: ExtractionResult):
            updated_relationships = []
            for relationship in result.relationships:
                source_entity = next(
                    (e for e in result.entities if e.name == relationship.source_name),
                    None,
                )
                target_entity = next(
                    (e for e in result.entities if e.name == relationship.target_name),
                    None,
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
            return ExtractionResult(
                entities=result.entities, relationships=updated_relationships
            )

        return prompt | self.llm | self.parser | RunnableLambda(update_relationships)

    def extract(self, chunks: list[TextChunk]) -> list[ExtractionResult]:
        chain = self.extract_chain()
        return chain.batch([{"text": chunk.content} for chunk in chunks])

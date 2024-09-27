from src.config import ETLConfig
from src.models import Entity, Relationship, TextChunk, Document
from neo4j import GraphDatabase


class Neo4JQueryManager:
    @staticmethod
    def create_document():
        return """
        MERGE (d:Document {id: $id})
        SET d += $properties
        """

    @staticmethod
    def create_entity():
        return """
        MERGE (e:Entity {id: $id})
        SET e += $properties
        """

    @staticmethod
    def create_relationship():
        return """
        MATCH (s:Entity {id: $source_id})
        MATCH (t:Entity {id: $target_id})
        MERGE (s)-[r:RELATES {type: $rel_type}]->(t)
        SET r += $properties
        """

    @staticmethod
    def create_chunk_and_relationships():
        return """
        CREATE (c:TextChunk {id: $id, text: $text, embedding: $embedding})
        WITH c
        MATCH (d:Document {id: $doc_id})
        CREATE (d)-[:HAS_CHUNK]->(c)
        WITH c
        UNWIND $entity_ids as entity_id
        MATCH (e:Entity {id: entity_id})
        CREATE (c)-[:CONTAINS]->(e)
        """


class KnowledgeGraphLoader:
    def __init__(self, config: ETLConfig):
        self.config = config
        self.driver = GraphDatabase.driver(
            config.graph_db_config.uri,
            auth=(
                config.graph_db_config.user,
                config.graph_db_config.password,
            ),
        )

    def load_document(self, document: Document) -> None:
        with self.driver.session() as session:
            session.run(
                Neo4JQueryManager.create_document(),
                id=document.id,
                properties=document.dict(),
            )

    def load_entities(self, entities: list[Entity]) -> None:
        with self.driver.session() as session:
            for entity in entities:
                session.run(
                    Neo4JQueryManager.create_entity(),
                    id=entity.id,
                    properties=entity.dict(),
                )

    def load_relationships(self, relationships: list[Relationship]) -> None:
        with self.driver.session() as session:
            for rel in relationships:
                session.run(
                    Neo4JQueryManager.create_relationship(),
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    rel_type=rel.type,
                    properties=rel.dict(),
                )

    def load_chunks(self, chunk: TextChunk, document: Document) -> None:
        with self.driver.session() as session:
            session.run(
                Neo4JQueryManager.create_chunk_and_relationships(),
                id=chunk.id,
                text=chunk.text,
                embedding=chunk.embedding,
                doc_id=document.id,
                entity_ids=[entity.id for entity in chunk.entities],
            )

    def load_incremental(
        self,
        entities: list[Entity],
        relationships: list[Relationship],
        chunks: TextChunk,
        document: Document,
    ) -> None:
        self.load_document(document)
        self.load_entities(entities)
        self.load_relationships(relationships)
        self.load_chunks(chunks, document)

    def close(self):
        self.driver.close()

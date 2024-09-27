from src.config import ETLConfig
from src.models import Entity, Relationship, TextChunk, Document
from neo4j import GraphDatabase


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

    def load_incremental(
        self,
        entities: list[Entity],
        relationships: list[Relationship],
        chunks: list[TextChunk],
        document: Document,
    ) -> None:
        with self.driver.session() as session:
            # Load document
            session.run(
                """
                MERGE (d:Document {id: $id})
                SET d += $properties
            """,
                id=document.id,
                properties=document.dict(),
            )

            # Load entities
            for entity in entities:
                session.run(
                    """
                    MERGE (e:Entity {id: $id})
                    SET e += $properties
                """,
                    id=entity.id,
                    properties=entity.dict(),
                )

            # Load relationships (both lexical and domain)
            for rel in relationships:
                session.run(
                    """
                    MATCH (s:Entity {id: $source_id})
                    MATCH (t:Entity {id: $target_id})
                    MERGE (s)-[r:RELATES {type: $rel_type}]->(t)
                    SET r += $properties
                """,
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    rel_type=rel.type,
                    properties=rel.dict(),
                )

            # Load chunks with embeddings and create relationships to entities and document
            for chunk in chunks:
                session.run(
                    """
                    CREATE (c:TextChunk {id: $id, text: $text, embedding: $embedding})
                    WITH c
                    MATCH (d:Document {id: $doc_id})
                    CREATE (d)-[:HAS_CHUNK]->(c)
                    WITH c
                    UNWIND $entity_ids as entity_id
                    MATCH (e:Entity {id: entity_id})
                    CREATE (c)-[:CONTAINS]->(e)
                """,
                    id=chunk.id,
                    text=chunk.text,
                    embedding=chunk.embedding,
                    doc_id=document.id,
                    entity_ids=[entity.id for entity in chunk.entities],
                )

    def close(self):
        self.driver.close()

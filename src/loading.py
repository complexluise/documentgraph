import logging

from src.config import ETLConfig
from src.models import Entity, Relationship, TextChunk, Document
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)


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
        CALL apoc.create.relationship(s, $rel_type, {}, t) YIELD rel
        RETURN rel
        """

    @staticmethod
    def create_chunks_and_relationships():
        return """
        UNWIND $chunks AS chunk
        CREATE (c:TextChunk {id: chunk.id, text: chunk.text, embedding: chunk.embedding})
        WITH c, chunk
        MATCH (d:Document {id: $doc_id})
        CREATE (d)-[:HAS_CHUNK]->(c)
        WITH c, chunk
        UNWIND chunk.entity_ids AS entity_id
        MATCH (e:Entity {id: entity_id})
        CREATE (c)-[:CONTAINS]->(e)
        WITH c, chunk
        MATCH (prev:TextChunk {id: chunk.prev_chunk_id})
        WHERE chunk.prev_chunk_id IS NOT NULL
        CREATE (prev)-[:NEXT]->(c)
        """


class KnowledgeGraphLoader:
    """
    Clase para cargar datos en un grafo de conocimiento Neo4j.

    Esta clase proporciona métodos para cargar documentos, entidades, relaciones y
    fragmentos de texto en una base de datos Neo4j, facilitando la construcción
    de un grafo de conocimiento.

    Attributes:
        config (ETLConfig): Configuración para la conexión a la base de datos.
        driver (neo4j.Driver): Driver para la conexión a Neo4j.
    """

    def __init__(self, config: ETLConfig):
        """
        Inicializa el KnowledgeGraphLoader.

        Args:
            config (ETLConfig): Configuración para la conexión a la base de datos Neo4j.
        """
        self.config = config
        self.driver = GraphDatabase.driver(
            config.graph_db_config.uri,
            auth=(config.graph_db_config.user, config.graph_db_config.password),
        )

    def load_document(self, document: Document) -> None:
        """
        Carga un documento en el grafo de conocimiento.

        Args:
            document (Document): El documento a cargar.

        Raises:
            Exception: Si ocurre un error durante la carga del documento.
        """
        properties = document.dict(exclude_none=True)
        del properties["content"]
        if "metadata" in properties and not properties["metadata"]:
            del properties["metadata"]

        try:
            with self.driver.session() as session:
                session.run(
                    Neo4JQueryManager.create_document(),
                    id=document.id,
                    properties=properties,
                )
            logger.info(f"Documento cargado exitosamente: {document.id}")
        except Exception as e:
            logger.error(f"Error al cargar el documento {document.id}: {str(e)}")
            raise

    def load_entities(self, entities: list[Entity]) -> None:
        with self.driver.session() as session:
            for entity in entities:
                entity_dict = entity.dict(exclude_none=True)
                if "properties" in entity_dict:
                    del entity_dict["properties"]

                session.run(
                    Neo4JQueryManager.create_entity(),
                    id=entity.id,
                    properties=entity_dict,
                )

    def load_relationships(self, relationships: list[Relationship]) -> None:
        with self.driver.session() as session:
            for rel in relationships:
                rel = rel.dict(exclude_none=True)
                if "properties" in rel and not rel["properties"]:
                    del rel["properties"]
                session.run(
                    Neo4JQueryManager.create_relationship(),
                    source_id=rel["source_id"],
                    target_id=rel["target_id"],
                    rel_type=rel["type"]
                )

    def load_chunk(self, chunk: TextChunk, document: Document, entities: list[Entity],
                   prev_chunk_id: str = None) -> None:
        """
        Carga fragmentos de texto en el grafo de conocimiento.
        Args:
            chunk (TextChunk): El fragmento de texto a cargar.
            document (Document): El documento al que pertenece el fragmento.
            entities (list[Entity]): Las entidades asociadas al fragmento.
            prev_chunk_id (str, optional): El ID del fragmento previo.

        """
        try:
            with self.driver.session() as session:

                chunk_data = {
                    "id": chunk.id,
                    "text": chunk.content,
                    "embedding": chunk.embedding,
                    "entity_ids": [entity.id for entity in entities],
                    "prev_chunk_id": prev_chunk_id,
                }

                session.run(
                    Neo4JQueryManager.create_chunks_and_relationships(),
                    chunks=chunk_data,
                    doc_id=document.id,
                )
            logger.info(f"Cargado chunk {chunk.id} fragmentos exitosamente")
        except Exception as e:
            logger.error(f"Error al cargar fragmentos: {str(e)}")
            raise

    def close(self):
        """
        Cierra la conexión con la base de datos Neo4j.
        """
        self.driver.close()

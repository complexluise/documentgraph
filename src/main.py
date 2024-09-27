import logging
from typing import List, Tuple
from src.extraction import DocumentExtractor
from src.models import Document, TextChunk, Entity, Relationship
from src.transformation import (
    TextPreprocessor,
    EmbeddingGenerator,
    EntityRelationExtractor,
)
from src.loading import KnowledgeGraphLoader
from src.query import QueryEngine
from src.config import ETLConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentAnalysisPipeline:
    def __init__(self, config: ETLConfig):
        self.config = config
        self.extractor = DocumentExtractor(config)
        self.preprocessor = TextPreprocessor(config)
        self.embedding_generator = EmbeddingGenerator(config)
        self.entity_relation_extractor = EntityRelationExtractor(config)
        self.graph_loader = KnowledgeGraphLoader(config)
        self.query_engine = QueryEngine(config)

    def execute_pipeline(self, data_sources: List[str]) -> None:
        """
        Ejecuta el pipeline ETL completo para análisis de documentos.
        """
        logger.info("Iniciando pipeline de análisis de documentos")
        try:
            for document in self.extract_documents(data_sources):
                logger.info(f"Extrayendo documento: {document.filename}")
                preprocessed_document = self.preprocess_documents(document)
                text_chunks = self.chunk_documents(preprocessed_document)
                embedded_chunks = self.generate_embeddings(text_chunks)
                entities, relationships = self.extract_entities_and_relationships(
                    embedded_chunks
                )
                self.load_knowledge_graph(entities, relationships, embedded_chunks)

            logger.info("Pipeline de análisis de documentos completado con éxito")
        except Exception as e:
            logger.error(f"Error en el pipeline de análisis: {str(e)}", exc_info=True)
            raise

    def extract_documents(self, data_sources: List[str]) -> List[Document]:
        """
        Extrae documentos de las fuentes de datos proporcionadas.
        """
        logger.info("Extrayendo documentos de las fuentes de datos")
        extracted_documents = []
        for source in data_sources:
            try:
                extracted_documents.append(self.extractor.extract(source))
            except Exception as e:
                logger.error(f"Error al extraer de {source}: {str(e)}")
        return extracted_documents

    def preprocess_documents(self, document: Document) -> Document:
        """
        Preprocesa los documentos extraídos.
        """
        logger.info("Preprocesando documentos")
        return self.preprocessor.preprocess(document)

    def chunk_documents(self, document: Document) -> List[TextChunk]:
        """
        Divide los documentos preprocesados en chunks de texto.
        """
        logger.info("Dividiendo documentos en chunks")
        return self.preprocessor.create_chunks(document)

    def generate_embeddings(self, text_chunks: List[TextChunk]) -> List[TextChunk]:
        """
        Genera embeddings para los chunks de texto.
        """
        logger.info("Generando embeddings para los chunks")
        return [
            chunk.model_copy(
                update={"embedding": self.embedding_generator.generate(chunk)}
            )
            for chunk in text_chunks
        ]

    def extract_entities_and_relationships(
        self, embedded_chunks: List[TextChunk]
    ) -> Tuple[List[Entity], List[Relationship]]:
        """
        Extrae entidades y relaciones de los chunks con embeddings.
        """
        logger.info("Extrayendo entidades y relaciones")
        entities, relationships = [], []
        for chunk in embedded_chunks:
            chunk_entities, chunk_relationships = (
                self.entity_relation_extractor.extract(chunk)
            )
            entities.extend(chunk_entities)
            relationships.extend(chunk_relationships)
        return entities, relationships

    def load_knowledge_graph(
        self,
        entities: List[Entity],
        relationships: List[Relationship],
        embedded_chunks: List[TextChunk],
    ) -> None:
        """
        Carga los datos extraídos en el grafo de conocimiento.
        """
        logger.info("Cargando datos en el grafo de conocimiento")
        self.graph_loader.load_incremental(entities, relationships, embedded_chunks)

    def process_query(self, query: str) -> str:
        """
        Procesa consultas de usuario utilizando el grafo de conocimiento.
        """
        logger.info(f"Procesando consulta de usuario: {query}")
        try:
            return self.query_engine.process_query(query)
        except Exception as e:
            logger.error(f"Error al procesar la consulta: {str(e)}", exc_info=True)
            return "Se produjo un error al procesar su consulta. Por favor, inténtelo de nuevo."


if __name__ == "__main__":
    etl_config = ETLConfig()  # Asume que ETLConfig puede ser instanciada sin argumentos
    pipeline = DocumentAnalysisPipeline(etl_config)
    # Aquí puedes agregar código para ejecutar el pipeline o manejar consultas

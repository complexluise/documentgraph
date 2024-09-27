import logging
from typing import Tuple
from src.extraction import DocumentExtractor
from src.models import Document, TextChunk, Entity, Relationship, ExtractionResult
from src.transformation import (
    TextProcessor,
    EmbeddingGenerator,
    EntityRelationExtractor,
)
from src.loading import KnowledgeGraphLoader
from src.config import ETLConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentAnalysisPipeline:
    def __init__(self, etl_config: ETLConfig):
        self.config = etl_config
        self.extractor = DocumentExtractor(etl_config)
        self.preprocessor = TextProcessor(etl_config)
        self.embedding_generator = EmbeddingGenerator(etl_config)
        self.entity_relation_extractor = EntityRelationExtractor(etl_config)
        self.graph_loader = KnowledgeGraphLoader(etl_config)

    def execute_pipeline(self, input_folder: str) -> None:
        """
        Ejecuta el pipeline ETL completo para análisis de documentos.
        """
        logger.info("Iniciando pipeline de análisis de documentos")
        try:
            for document in self.extract_documents(input_folder):
                logger.info(f"Extrayendo documento: {document.filename}")
                preprocessed_document = self.preprocess_documents(document)
                text_chunks = self.chunk_documents(preprocessed_document)
                embedded_chunks = self.generate_embeddings(text_chunks)
                extraction_results = self.extract_entities_and_relationships(
                    embedded_chunks
                )
                self.load_knowledge_graph(extraction_results, embedded_chunks, document)

            logger.info("Pipeline de análisis de documentos completado con éxito")
        except Exception as e:
            logger.error(f"Error en el pipeline de análisis: {str(e)}", exc_info=True)
            raise

    def extract_documents(self, input_folder: str) -> Document:
        """
        Extrae documentos de las fuentes de datos proporcionadas.
        """
        logger.info("Extrayendo documentos de las fuentes de datos")
        return self.extractor.extract(input_folder)

    def preprocess_documents(self, document: Document) -> Document:
        """
        Preprocesa los documentos extraídos.
        """
        logger.info("Preprocesando documentos")
        return self.preprocessor.process(document)

    def chunk_documents(self, document: Document) -> list[TextChunk]:
        """
        Divide los documentos preprocesados en chunks de texto.
        """
        logger.info("Dividiendo documentos en chunks")
        return self.preprocessor.create_chunks(document)

    def generate_embeddings(self, text_chunks: list[TextChunk]) -> list[TextChunk]:
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
        self, embedded_chunks: list[TextChunk]
    ) -> list[ExtractionResult]:
        """
        Extrae entidades y relaciones de los chunks con embeddings.
        """
        logger.info("Extrayendo entidades y relaciones")
        return self.entity_relation_extractor.extract(embedded_chunks)

    def load_knowledge_graph(
        self,
        extraction_results: list[ExtractionResult],
        embedded_chunks: list[TextChunk],
        document: Document,
    ) -> None:
        """
        Carga los datos extraídos en el grafo de conocimiento.
        """
        logger.info("Cargando datos en el grafo de conocimiento")
        try:
            for i, result in enumerate(extraction_results):
                self.graph_loader.load_incremental(  # TODO terminar de probar
                    result.entities, result.relationships, embedded_chunks[i], document
                )
            logger.info("Datos cargados exitosamente en el grafo de conocimiento")
        except Exception as e:
            logger.error(f"Error al cargar datos en el grafo: {str(e)}", exc_info=True)
        finally:
            self.graph_loader.close()


if __name__ == "__main__":
    etl_config = ETLConfig()  # Asume que ETLConfig puede ser instanciada sin argumentos
    pipeline = DocumentAnalysisPipeline(etl_config)
    pipeline.execute_pipeline("data")

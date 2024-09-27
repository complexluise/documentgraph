import logging
from typing import List, Tuple
from src.extraction import DataExtractor
from src.models import Document, Chunk, Entity, Relationship
from src.transformation import TextProcessor, EmbeddingGenerator, EntityRelationAnalyzer
from src.loading import GraphLoader
from src.query import QueryManager
from src.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenAIApplication:
    def __init__(self, config: Config):
        self.config = config
        self.extractor = DataExtractor(config)
        self.processor = TextProcessor(config)
        self.embedding_generator = EmbeddingGenerator(config)
        self.analyzer = EntityRelationAnalyzer(config)
        self.loader = GraphLoader(config)
        self.query_manager = QueryManager(config)

    def run_pipeline(self, sources: List[str]) -> None:
        """
        Ejecuta el pipeline ETL completo.
        """
        logger.info("Starting ETL pipeline")
        try:
            documents = self.extract_data(sources)
            processed_docs = self.process_documents(documents)
            chunks = self.create_chunks(processed_docs)
            enriched_chunks = self.enrich_chunks(chunks)
            entities, relationships = self.analyze_chunks(enriched_chunks)
            self.load_to_graph(entities, relationships, chunks)
            logger.info("ETL pipeline completed successfully")
        except Exception as e:
            logger.error(f"Error in ETL pipeline: {str(e)}", exc_info=True)
            raise

    def extract_data(self, sources: List[str]) -> List[Document]:
        """
        Extrae datos de las fuentes proporcionadas.
        """
        logger.info("Extracting data from sources")
        documents = []
        for source in sources:
            try:
                documents.append(self.extractor.extract(source))
            except Exception as e:
                logger.error(f"Error extracting from {source}: {str(e)}")
        return documents

    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Procesa los documentos extraídos.
        """
        logger.info("Processing documents")
        return [self.processor.process(doc) for doc in documents]

    def create_chunks(self, documents: List[Document]) -> List[Chunk]:
        """
        Crea chunks a partir de los documentos procesados.
        """
        logger.info("Creating chunks from documents")
        chunks = []
        for doc in documents:
            chunks.extend(self.processor.create_chunks(doc))
        return chunks

    def enrich_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Enriquece los chunks con embeddings.
        """
        logger.info("Enriching chunks with embeddings")
        return [self.embedding_generator.generate(chunk) for chunk in chunks]

    def analyze_chunks(self, chunks: List[Chunk]) -> Tuple[List[Entity], List[Relationship]]:
        """
        Analiza los chunks para extraer entidades y relaciones.
        """
        logger.info("Analyzing chunks for entities and relationships")
        entities, relationships = [], []
        for chunk in chunks:
            chunk_entities, chunk_relationships = self.analyzer.analyze(chunk)
            entities.extend(chunk_entities)
            relationships.extend(chunk_relationships)
        return entities, relationships

    def load_to_graph(self, entities: List[Entity], relationships: List[Relationship], chunks: List[Chunk]) -> None:
        """
        Carga los datos en la base de datos de grafos.
        """
        logger.info("Loading data to graph database")
        self.loader.load_incremental(entities, relationships, chunks)

    def handle_user_query(self, query: str) -> str:
        """
        Maneja las consultas de usuario.
        """
        logger.info(f"Handling user query: {query}")
        try:
            return self.query_manager.process_query(query)
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return "An error occurred while processing your query. Please try again."

if __name__ == "__main__":
    config = Config()  # Asume que Config puede ser instanciada sin argumentos
    app = GenAIApplication(config)
    # Aquí puedes agregar código para ejecutar el pipeline o manejar consultas

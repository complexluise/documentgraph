# DocumentGraph: An ETL Pipeline for Document Analysis with Neo4j

## Overview

**DocumentGraph** is a Python package designed for end-to-end document analysis, using an ETL (Extract, Transform, Load) pipeline to process textual documents and represent the extracted information in a **Neo4j knowledge graph**. The package extracts text from documents, preprocesses and chunks the content, generates embeddings, and identifies entities and relationships within the text. These entities, relationships, and text chunks are then loaded into a Neo4j graph database for advanced analysis and querying.

This package is ideal for users who need to process large volumes of documents and structure them into a graph-based knowledge representation, where entities and their relationships can be explored and queried efficiently.

### Key Features
- **Document extraction**: Loads documents from a specified input folder.
- **Text preprocessing**: Cleans and chunks the document into smaller, meaningful pieces.
- **Embedding generation**: Generates vector representations for text chunks.
- **Entity and relationship extraction**: Detects entities and relationships within the text using a knowledge extraction model.
- **Knowledge graph loading**: Loads documents, text chunks, entities, and relationships into a **Neo4j** graph database.
  
### Limitations
- The package assumes that the input documents are in `.txt` format.
- Preprocessing and extraction pipelines are designed for text data only.
- The performance depends on the quality of the pre-trained embedding models and entity extraction logic.
- Neo4j must be set up and running (locally or via AuraDB) with proper credentials for the package to function.

## Prerequisites

### 1. Python Environment
Ensure you have **Python 3.10+** installed in your environment. You can create a virtual environment to manage dependencies easily:

```bash
python -m venv documentgraph-env
source documentgraph-env/bin/activate   # On Windows: documentgraph-env\Scripts\activate
```

### 2. Required Python Packages
Install the required dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

These packages include libraries for Neo4j, logging, and document extraction.

### 3. Neo4j Setup
The package requires a **Neo4j** database to store and query the knowledge graph. You can either use **Neo4j Aura** (cloud-based) or run a **local Neo4j instance**.

#### Option 1: Neo4j Aura (Cloud-based)
- Sign up for a free or paid **Neo4j Aura** account at [https://aura.neo4j.io/](https://aura.neo4j.io/).
- Create a new Neo4j project and note down the `uri`, `username`, and `password` for connection.

#### Option 2: Local Neo4j Instance
- Download and install **Neo4j Desktop** from [https://neo4j.com/download/](https://neo4j.com/download/).
- Start a new local graph database instance.
- The default local connection `uri` is usually `bolt://localhost:7687`, and the default username/password is `neo4j/neo4j`.

### 4. Environment Variables
You need to set up environment variables to allow the package to connect to the Neo4j database. You can add these variables to your shell environment or use a `.env` file.

```bash
export NEO4J_URI=bolt://localhost:7687  # For local Neo4j instance
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password
export OPENAI_API_KEY=your-openai-api-key
```

If you are using **Neo4j Aura**, replace the URI and credentials accordingly:

```bash
export NEO4J_URI=neo4j+s://your-aura-database-uri
export NEO4J_USER=your-username
export NEO4J_PASSWORD=your-password
export OPENAI_API_KEY=your-openai-api-key
```

### 5. Additional Neo4j Configuration
For proper relationship creation, ensure you have the APOC (Awesome Procedures on Cypher) plugin installed in your Neo4j instance. This is necessary for creating custom relationships between entities and text chunks.

## Usage

### 1. Setting up the ETL Pipeline

```python
from documentgraph import ETLConfig, DocumentAnalysisPipeline

# Create an ETLConfig with Neo4j credentials
etl_config = ETLConfig()

# Initialize the ETL pipeline
pipeline = DocumentAnalysisPipeline(etl_config)

# Execute the pipeline with the input folder containing text documents
pipeline.execute_pipeline(input_folder="path/to/your/text/files")
```

### 2. Pipeline Workflow

1. **Document Extraction**: The pipeline reads all `.txt` files from the specified input folder.
2. **Text Preprocessing**: The text is cleaned and broken down into smaller chunks.
3. **Embedding Generation**: Each chunk gets converted into a vector using a pre-trained embedding model.
4. **Entity and Relationship Extraction**: Entities and relationships between them are identified within the chunks.
5. **Knowledge Graph Loading**: The extracted entities, relationships, and chunks are saved in the Neo4j knowledge graph.

### 3. Querying the Knowledge Graph

Once the pipeline has processed the documents and loaded the data into Neo4j, you can query the graph for insights using **Cypher**.

For example, to retrieve all entities in the graph:

```cypher
MATCH (e:Entity) RETURN e LIMIT 10;
```

To retrieve relationships between entities:

```cypher
MATCH (e1:Entity)-[r]->(e2:Entity) RETURN e1, r, e2 LIMIT 10;
```

## Contributing

We welcome contributions to DocumentGraph! Here's how you can help:

### Reporting Issues

If you encounter any bugs or have suggestions for improvements:

1. Check the [existing issues](https://github.com/yourusername/documentgraph/issues) to avoid duplicates.
2. If your issue isn't already listed, [open a new issue](https://github.com/yourusername/documentgraph/issues/new).
3. Clearly describe the problem or enhancement, including steps to reproduce if applicable.
4. Add relevant labels (e.g., 'bug', 'enhancement', 'documentation').

### Making Enhancements

To contribute code or documentation improvements:

1. Fork the repository.
2. Create a new branch for your feature: `git checkout -b feature/your-feature-name`.
3. Make your changes, ensuring you follow the project's coding standards.
4. Write or update tests as necessary.
5. Commit your changes with clear, descriptive commit messages.
6. Push to your fork and [submit a pull request](https://github.com/yourusername/documentgraph/compare).

### Proposing Major Changes

For significant changes that could alter the project's direction:

1. Open an issue to discuss your proposal before starting work.
2. Outline the rationale and implementation details of your proposal.
3. Engage in discussion with maintainers and the community.
4. If approved, follow the process for making enhancements.

We appreciate your contributions to making DocumentGraph better!


## License

DocumentGraph is licensed under the **Apache License Version 2.0**.

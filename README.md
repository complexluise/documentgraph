# DocumentGraph

DocumentGraph es una herramienta de análisis de documentos que utiliza técnicas de procesamiento de lenguaje natural y grafos de conocimiento para extraer información valiosa de tus documentos.

## Características

- Extracción de documentos solo .txt
- Preprocesamiento de texto
- Generación de embeddings para chunks de texto
- Extracción de entidades y relaciones
- Carga de datos en un grafo de conocimiento

## Instalación

```bash
pip install documentgraph
```

## Uso

```python
from documentgraph import DocumentAnalysisPipeline, ETLConfig

# Configurar el pipeline
etl_config = ETLConfig()
pipeline = DocumentAnalysisPipeline(etl_config)

# Ejecutar el pipeline
pipeline.execute_pipeline("ruta/a/tus/documentos")
```

# Estructura del Proyecto
* src/: Contiene el código fuente del proyecto
* extraction.py: Módulo para la extracción de documentos
* models.py: Definiciones de modelos de datos
* transformation.py: Módulos para el procesamiento de texto, generación de embeddings y extracción de entidades/relaciones
* loading.py: Módulo para cargar datos en el grafo de conocimiento
* config.py: Configuración del pipeline ETL
* main.py: Punto de entrada principal y definición del pipeline

# Configuración
La configuración del pipeline se realiza a través de la clase ETLConfig. Asegúrate de configurar correctamente los parámetros antes de ejecutar el pipeline.

# Contribuir
Las contribuciones son bienvenidas. Por favor, abre un issue para discutir los cambios propuestos antes de enviar un pull request.

# Licencia
Este proyecto está licenciado bajo la Licencia Apache 2.0. Consulta el archivo LICENSE para más detalles.
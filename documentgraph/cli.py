import argparse
from documentgraph import DocumentAnalysisPipeline, ETLConfig


def main():
    parser = argparse.ArgumentParser(description="Document Analysis Pipeline CLI")
    parser.add_argument("input_folder", help="Path to the input folder containing documents")
    parser.add_argument("--config", help="Path to the ETL configuration file", default="etl_config.yaml")

    args = parser.parse_args()

    # Load ETL configuration
    etl_config = ETLConfig.from_yaml(args.config)

    # Initialize the pipeline
    pipeline = DocumentAnalysisPipeline(etl_config)

    # Execute the pipeline
    pipeline.execute_pipeline(args.input_folder)

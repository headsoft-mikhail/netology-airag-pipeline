import argparse
import typing
from pathlib import Path

from rag_prep.config import load_config
from rag_prep.pipeline import RAGPipeline


def main() -> None:
    parser: typing.Final = argparse.ArgumentParser(description="Prepare documents for RAG pipeline")

    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/default.yaml"),
        help="Path to pipeline configuration",
    )

    args: typing.Final = parser.parse_args()
    config: typing.Final = load_config(args.config)

    pipeline: typing.Final = RAGPipeline(config)
    pipeline.run()

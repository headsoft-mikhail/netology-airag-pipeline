import argparse
import typing
from pathlib import Path

from rag.config import load_config
from rag.pipelines.prepare.pipeline import RAGPreparePipeline


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

    pipeline: typing.Final = RAGPreparePipeline(config)
    pipeline.run()

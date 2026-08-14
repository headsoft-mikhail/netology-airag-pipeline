import argparse
import typing
from pathlib import Path

from rag.config import load_config
from rag.pipelines.chunk.pipeline import RAGChunkPipeline
from rag.pipelines.embeddings.pipeline import RAGEmbeddingsPipeline
from rag.pipelines.prepare.pipeline import RAGPreparePipeline
from rag.pipelines.vector_store.pipeline import RAGVectorStorePipeline


def main() -> None:
    parser: typing.Final = argparse.ArgumentParser(
        description="RAG data preparation pipeline",
    )

    subparsers: typing.Final = parser.add_subparsers(
        dest="command",
        required=True,
    )

    prepare_parser: typing.Final = subparsers.add_parser(
        "prepare",
        help="Prepare raw documents",
    )
    prepare_parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/default.yaml"),
        help="Path to pipeline configuration",
    )

    chunk_parser: typing.Final = subparsers.add_parser(
        "chunk",
        help="Split prepared documents into chunks",
    )
    chunk_parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/default.yaml"),
        help="Path to pipeline configuration",
    )

    embedding_parser: typing.Final = subparsers.add_parser(
        "embedding",
        help="Prepare embeddings",
    )
    embedding_parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/default.yaml"),
        help="Path to pipeline configuration",
    )

    vector_store_parser: typing.Final = subparsers.add_parser(
        "vector_store",
        help="Prepare vector store",
    )
    vector_store_parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/default.yaml"),
        help="Path to pipeline configuration",
    )

    args: typing.Final = parser.parse_args()
    config: typing.Final = load_config(args.config)

    if args.command == "prepare":
        pipeline = RAGPreparePipeline(config)
    elif args.command == "chunk":
        pipeline = RAGChunkPipeline(config)
    elif args.command == "embedding":
        pipeline = RAGEmbeddingsPipeline(config)
    elif args.command == "vector_store":
        pipeline = RAGVectorStorePipeline(config)
    else:
        raise ValueError(f"Unknown command: {args.command}")

    pipeline.run()

import logging
import typing

from rag.config import PipelineConfig
from rag.pipelines.chunk.stages.exporter import ChunkExporter
from rag.pipelines.chunk.stages.loader import load_documents
from rag.pipelines.chunk.stages.splitter import ChunkSplitter

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


class RAGChunkPipeline:
    def __init__(self, config: PipelineConfig):
        self.config: PipelineConfig = config

        self.splitter = ChunkSplitter(config=self.config.chunking)
        self.exporter = ChunkExporter(output_dir=config.paths.chunks)

    def run(self) -> None:
        LOGGER_OBJ.info("Start chunking pipeline...")

        documents: typing.Final = load_documents(input_path=self.config.paths.prepared_jsonl)
        LOGGER_OBJ.info("Loading - DONE!\n-------------")

        chunks: typing.Final = self.splitter.split_documents(documents)
        LOGGER_OBJ.info(f"Splitting - DONE! {len(chunks)} chunks created.\n-------------")

        self.exporter.export(chunks)

        LOGGER_OBJ.info("Exporting - DONE!")

        LOGGER_OBJ.info("-------------")

        LOGGER_OBJ.info("DONE!")

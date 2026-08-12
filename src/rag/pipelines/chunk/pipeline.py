import datetime as dt
import logging
import typing

from rag.config import PipelineConfig
from rag.manifest import ManifestManager, StagesEnum
from rag.pipelines.chunk.stages.exporter import ChunkExporter
from rag.pipelines.chunk.stages.loader import load_documents
from rag.pipelines.chunk.stages.splitter import ChunkSplitter
from rag.pipelines.chunk.stages.validator import ChunkValidator

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


class RAGChunkPipeline:
    def __init__(self, config: PipelineConfig):
        self.config: PipelineConfig = config

        self.splitter = ChunkSplitter(config=self.config.chunking)
        self.exporter = ChunkExporter(output_dir=self.config.paths.chunks)
        self.validator = ChunkValidator(config=self.config.chunking)
        self.manifest_manager = ManifestManager(config=self.config)

    def run(self) -> None:
        LOGGER_OBJ.info("Start chunking pipeline...")
        started_at: typing.Final = dt.datetime.now(tz=dt.UTC).isoformat()

        documents: typing.Final = load_documents(input_path=self.config.paths.prepared_jsonl)
        LOGGER_OBJ.info("Loading - DONE!\n-------------")

        chunks: typing.Final = self.splitter.split_documents(documents)
        LOGGER_OBJ.info(f"Splitting - DONE! {len(chunks)} chunks created.\n-------------")

        self.exporter.export(chunks)

        LOGGER_OBJ.info("Exporting - DONE!\n-------------")

        validation_metrics: typing.Final = self.validator.validate(chunks=chunks, documents=documents)
        if not validation_metrics.valid:
            LOGGER_OBJ.error(f"Chunk validation failed: {validation_metrics}")
        LOGGER_OBJ.info("Validation - DONE!\n-------------")

        self.manifest_manager.create_stage_manifest(
            stage=StagesEnum.CHUNK,
            started_at=started_at,
            prepared_documents=documents,
            chunks=chunks,
            validation_metrics=validation_metrics,
        )

        LOGGER_OBJ.info("DONE!")

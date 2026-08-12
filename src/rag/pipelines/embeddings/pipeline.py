import datetime as dt
import logging
import typing

from rag.config import PipelineConfig
from rag.manifest import ManifestManager, StagesEnum
from rag.pipelines.embeddings.stages.embedding import EmbeddingModel, EmbeddingStage
from rag.pipelines.embeddings.stages.exporter import EmbeddingExporter
from rag.pipelines.embeddings.stages.loader import load_chunks
from rag.pipelines.embeddings.stages.validator import EmbeddingValidator

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


class RAGEmbeddingsPipeline:
    def __init__(self, config: PipelineConfig):
        self.config: PipelineConfig = config

        self.embedding_model = EmbeddingModel(
            model_name=self.config.embedding.model,
            transformer=self.config.embedding.transformer,
        )
        self.embedding_stage = EmbeddingStage(model=self.embedding_model)
        self.validator = EmbeddingValidator(
            model_name=self.embedding_model.model_name,
            dimensions=self.embedding_model.dimensions,
        )
        self.manifest_manager = ManifestManager(config=self.config)
        self.exporter = EmbeddingExporter(output_dir=self.config.paths.embeddings)

    def run(self) -> None:
        LOGGER_OBJ.info("Start embedding pipeline...")
        started_at: typing.Final = dt.datetime.now(tz=dt.UTC).isoformat()

        chunks: typing.Final = load_chunks(input_path=self.config.paths.chunks_jsonl)
        LOGGER_OBJ.info("Loading - DONE!\n-------------")

        embedded_chunks: typing.Final = self.embedding_stage.run(chunks)
        LOGGER_OBJ.info("Embedding - DONE!\n-------------")

        self.exporter.export(embeddings=embedded_chunks)
        LOGGER_OBJ.info("Exporting - DONE!\n-------------")

        validation_metrics: typing.Final = self.validator.validate(chunks=chunks, embeddings=embedded_chunks)
        LOGGER_OBJ.info("Validation - DONE!\n-------------")

        self.manifest_manager.create_stage_manifest(
            stage=StagesEnum.EMBEDDING,
            started_at=started_at,
            chunks=chunks,
            embedded_chunks=embedded_chunks,
            validation_metrics=validation_metrics,
        )

        LOGGER_OBJ.info("DONE!")

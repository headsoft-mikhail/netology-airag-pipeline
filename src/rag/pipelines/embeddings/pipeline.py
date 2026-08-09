import logging
import typing

from rag.config import PipelineConfig
from rag.pipelines.embeddings.stages.loader import load_chunks

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


class RAGEmbeddingsPipeline:
    def __init__(self, config: PipelineConfig):
        self.config: PipelineConfig = config

    def run(self) -> None:
        LOGGER_OBJ.info("Start embedding pipeline...")

        load_chunks(input_path=self.config.paths.chunks_jsonl)
        LOGGER_OBJ.info("Loading - DONE!\n-------------")

        LOGGER_OBJ.info("DONE!")

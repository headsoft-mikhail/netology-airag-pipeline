import datetime as dt
import logging
import typing

from rag.config import PipelineConfig
from rag.manifest import ManifestManager, StagesEnum
from rag.pipelines.prepare.stages.cleaner import TextCleaner
from rag.pipelines.prepare.stages.deduplication import Deduplicator
from rag.pipelines.prepare.stages.exporter import DatasetExporter
from rag.pipelines.prepare.stages.loader import load_documents
from rag.pipelines.prepare.stages.normalizer import TextNormalizer
from rag.pipelines.prepare.stages.parser import parse_document
from rag.pipelines.prepare.stages.structurer import DocumentStructurer

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


class RAGPreparePipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config

        self.normalizer = TextNormalizer(unicode_form=config.normalization.unicode_form)
        self.deduplicator = Deduplicator(
            near_duplicate_threshold=(config.deduplication.similarity_threshold),
        )
        self.structurer = DocumentStructurer()
        self.exporter = DatasetExporter(output_dir=config.paths.prepared)
        self.manifest_manager = ManifestManager(config=self.config)

    def run(self) -> None:
        LOGGER_OBJ.info("Start pipeline...")
        started_at: typing.Final = dt.datetime.now(tz=dt.UTC).isoformat()

        documents: typing.Final = load_documents(
            input_dir=self.config.paths.input,
            supported_formats=(self.config.parsing.supported_formats),
        )
        LOGGER_OBJ.info("Loading - DONE!\n-------------")

        parsed_documents: typing.Final = [parse_document(document) for document in documents]
        LOGGER_OBJ.info("Parsing - DONE!\n-------------")

        cleaned_documents: typing.Final = [TextCleaner.clean(document) for document in parsed_documents]
        LOGGER_OBJ.info("Cleaning - DONE!\n-------------")

        normalized_documents = [self.normalizer.normalize(document) for document in cleaned_documents]
        LOGGER_OBJ.info("Normalization - DONE!\n-------------")
        if self.config.cleaning.remove_empty_documents:
            normalized_documents = [one_document for one_document in normalized_documents if one_document.text.strip()]
        LOGGER_OBJ.info(
            "Removing empty documents - DONE! "
            f"{len(documents) - len(normalized_documents)} documents removed."
            "\n-------------"
        )

        deduplication_result: typing.Final = self.deduplicator.deduplicate(normalized_documents)
        LOGGER_OBJ.info(
            "Deduplication - DONE! "
            f"{len(normalized_documents) - len(deduplication_result.documents)} documents removed."
            "\n-------------"
        )

        structured_documents: typing.Final = self.structurer.structure_many(deduplication_result.documents)
        LOGGER_OBJ.info("Structurizing - DONE!\n-------------")

        LOGGER_OBJ.info("Exporting results...")
        self.exporter.export(structured_documents)

        self.manifest_manager.create_stage_manifest(
            stage=StagesEnum.PREPARE,
            started_at=started_at,
            raw_documents=documents,
            deduplication_result=deduplication_result,
        )

        LOGGER_OBJ.info("DONE!")

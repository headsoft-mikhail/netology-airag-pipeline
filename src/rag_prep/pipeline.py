import datetime as dt
import logging
import typing

from rag_prep.config import PipelineConfig
from rag_prep.manifest import Manifest
from rag_prep.stages.cleaner import TextCleaner
from rag_prep.stages.deduplication import Deduplicator
from rag_prep.stages.exporter import DatasetExporter
from rag_prep.stages.loader import load_documents
from rag_prep.stages.normalizer import TextNormalizer
from rag_prep.stages.parser import parse_document
from rag_prep.stages.structurer import DocumentStructurer

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config

        self.normalizer = TextNormalizer(unicode_form=config.normalization.unicode_form)
        self.deduplicator = Deduplicator(
            near_duplicate_threshold=(config.deduplication.similarity_threshold),
        )
        self.structurer = DocumentStructurer()
        self.exporter = DatasetExporter(output_dir=config.paths.output)

    def run(self) -> None:
        LOGGER_OBJ.info("Start pipeline...")
        started_at: typing.Final = dt.datetime.now(dt.UTC).isoformat()

        documents: typing.Final = load_documents(
            input_dir=self.config.paths.input,
            supported_formats=(self.config.parsing.supported_formats),
        )

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
            f"len(normalized_documents) - {len(deduplication_result.documents)} documents removed."
            "\n-------------"
        )

        structured_documents: typing.Final = self.structurer.structure_many(deduplication_result.documents)
        LOGGER_OBJ.info("Structurizing - DONE!\n-------------")

        LOGGER_OBJ.info("Exporting results...")
        self.exporter.export(structured_documents)

        LOGGER_OBJ.info("Exporting manifest...")
        Manifest(
            started_at=started_at,
            input_documents=len(documents),
            output_documents=len(deduplication_result.documents),
            exact_duplicates=deduplication_result.exact_duplicates,
            near_duplicates=deduplication_result.near_duplicates,
        ).save(self.exporter.output_dir / "manifest.json")

        LOGGER_OBJ.info("DONE!")

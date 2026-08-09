import hashlib
import logging
import re
import typing
from dataclasses import dataclass

from datasketch import MinHash

from rag import models

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


@dataclass(kw_only=True, slots=True, frozen=True)
class Deduplicator:
    near_duplicate_threshold: float = 0.85
    num_perm: int = 128

    def deduplicate(
        self,
        documents: list[models.ParsedDocument],
    ) -> models.DeduplicationResult:
        unique_documents: typing.Final[list[models.ParsedDocument]] = []
        exact_hashes: typing.Final[set[str]] = set()

        exact_duplicates = 0
        near_duplicates = 0

        for one_document in documents:
            text_hash = self._text_hash(one_document.text)

            if text_hash in exact_hashes:
                LOGGER_OBJ.info(f"Document {one_document.source} has exact duplicate")
                exact_duplicates += 1
                continue

            if self._is_near_duplicate(one_document, unique_documents):
                LOGGER_OBJ.info(f"Document {one_document.source} has near duplicate")
                near_duplicates += 1
                continue

            exact_hashes.add(text_hash)
            unique_documents.append(one_document)

        return models.DeduplicationResult(
            documents=unique_documents,
            exact_duplicates=exact_duplicates,
            near_duplicates=near_duplicates,
        )

    @staticmethod
    def _text_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _is_near_duplicate(
        self,
        document: models.ParsedDocument,
        existing_documents: list[models.ParsedDocument],
    ) -> bool:
        current: typing.Final = self._create_minhash(document.text)

        for one_existing_document in existing_documents:
            candidate = self._create_minhash(one_existing_document.text)
            similarity = current.jaccard(candidate)

            if similarity >= self.near_duplicate_threshold:
                return True

        return False

    def _create_minhash(self, text: str) -> MinHash:
        minhash: typing.Final = MinHash(num_perm=self.num_perm)
        words: typing.Final = self._tokenize(text)

        for one_word in words:
            minhash.update(one_word.encode("utf-8"))

        return minhash

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return set(re.findall(r"\w+", text.lower(), re.UNICODE))

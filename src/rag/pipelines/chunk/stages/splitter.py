import dataclasses
import hashlib
import re
import typing

from rag import models
from rag.config import ChunkingConfig


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class ChunkSplitter:
    config: ChunkingConfig

    _SENTENCE_PATTERN: typing.Final = re.compile(r"(?<=[.!?])(?:[»”\"])?\s+")

    def split_documents(self, documents: list[models.PreparedDocument]) -> list[models.Chunk]:
        chunks: typing.Final[list[models.Chunk]] = []

        for document in documents:
            chunks.extend(self.split_document(document))

        return chunks

    def split_document(self, document: models.PreparedDocument) -> list[models.Chunk]:
        sections: typing.Final = self._split_into_sections(document)

        chunks: typing.Final[list[models.Chunk]] = []

        for section_name, text in sections:
            sentences = self._split_sentences(text)
            section_chunks = self._build_chunks(
                sentences=sentences,
                document=document,
                section=section_name,
            )
            chunks.extend(section_chunks)

        return self._reindex_chunks(chunks)

    def _split_into_sections(self, document: models.PreparedDocument) -> list[tuple[str | None, str]]:
        text: typing.Final = document.text.strip()

        if not text:
            return []

        configured_sections: typing.Final = document.metadata.section

        if not configured_sections:
            return [(None, text)]

        lines: typing.Final = [line.strip() for line in text.splitlines() if line.strip()]

        sections: typing.Final[list[tuple[str | None, str]]] = []
        current_section: str | None = None
        current_lines: list[str] = []

        configured_section_set: typing.Final = set(configured_sections)

        for line in lines:
            if line in configured_section_set:
                if current_lines:
                    sections.append(
                        (
                            current_section,
                            "\n".join(current_lines),
                        )
                    )

                current_section = line
                current_lines = []
                continue

            current_lines.append(line)

        if current_lines:
            sections.append(
                (
                    current_section,
                    "\n".join(current_lines),
                )
            )

        return sections

    def _split_sentences(self, text: str) -> list[str]:
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return []

        sentences: typing.Final = self._SENTENCE_PATTERN.split(text)
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    def _build_chunks(
        self,
        sentences: list[str],
        document: models.PreparedDocument,
        section: str | None,
    ) -> list[models.Chunk]:
        chunks: typing.Final[list[models.Chunk]] = []

        current_sentences: list[str] = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)

            if sentence_tokens > self.config.chunk_size:
                if current_sentences:
                    chunks.append(
                        self._create_chunk(
                            sentences=current_sentences,
                            document=document,
                            section=section,
                        )
                    )

                    current_sentences = []
                    current_tokens = 0

                long_chunks = self._split_long_sentence(
                    sentence=sentence,
                    document=document,
                    section=section,
                )

                chunks.extend(long_chunks)
                continue

            if current_sentences and current_tokens + sentence_tokens > self.config.chunk_size:
                chunks.append(
                    self._create_chunk(
                        sentences=current_sentences,
                        document=document,
                        section=section,
                    )
                )

                overlap_sentences: list[str] = []
                overlap_tokens = 0

                for previous_sentence in reversed(current_sentences):
                    previous_tokens = self._count_tokens(previous_sentence)

                    if overlap_tokens + previous_tokens > self.config.chunk_overlap:
                        break

                    overlap_sentences.insert(0, previous_sentence)
                    overlap_tokens += previous_tokens

                current_sentences = overlap_sentences
                current_tokens = overlap_tokens

            current_sentences.append(sentence)
            current_tokens += sentence_tokens

        if current_sentences:
            chunks.append(
                self._create_chunk(
                    sentences=current_sentences,
                    document=document,
                    section=section,
                )
            )

        return chunks

    def _split_long_sentence(
        self,
        sentence: str,
        document: models.PreparedDocument,
        section: str | None,
    ) -> list[models.Chunk]:
        tokens: typing.Final = self.config.tokenizer.encode(sentence)
        chunks: typing.Final[list[models.Chunk]] = []
        start = 0
        tokens_count: typing.Final = len(tokens)

        while start < tokens_count:
            end = min(start + self.config.chunk_size, tokens_count)
            chunk_tokens = tokens[start:end]
            chunk_text = self.config.tokenizer.decode(chunk_tokens).strip()

            chunks.append(
                self._create_chunk(
                    sentences=[chunk_text],
                    document=document,
                    section=section,
                )
            )

            if end >= tokens_count:
                break

            start = end - self.config.chunk_overlap

        return chunks

    def _create_chunk(
        self,
        sentences: list[str],
        document: models.PreparedDocument,
        section: str | None,
    ) -> models.Chunk:
        text: typing.Final = " ".join(sentences).strip()
        token_count: typing.Final = self._count_tokens(text)
        text_hash: typing.Final = hashlib.sha256(text.encode("utf-8")).hexdigest()
        position: typing.Final = 0

        chunk_id: typing.Final = hashlib.sha256(
            f"{document.metadata.document_id}:{position}:{text_hash}".encode()
        ).hexdigest()

        metadata: typing.Final = models.ChunkMetadata(
            document_id=document.metadata.document_id,
            position=position,
            chunk_token_count=token_count,
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            chunking_strategy=self.config.strategy,
            source=document.metadata.source,
            section=section,
            text_hash=text_hash,
        )

        return models.Chunk(id=chunk_id, text=text, metadata=metadata)

    def _reindex_chunks(
        self,
        chunks: list[models.Chunk],
    ) -> list[models.Chunk]:
        result: typing.Final[list[models.Chunk]] = []

        for position, chunk in enumerate(chunks):
            metadata: models.ChunkMetadata = chunk.metadata.model_copy(update={"position": position})
            chunk_id: str = hashlib.sha256(
                f"{metadata.document_id}:{position}:{metadata.text_hash}".encode()
            ).hexdigest()
            result.append(chunk.model_copy(update={"id": chunk_id, "metadata": metadata}))

        return result

    def _count_tokens(self, text: str) -> int:
        return len(self.config.tokenizer.encode(text))

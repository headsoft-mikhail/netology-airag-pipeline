import dataclasses
import datetime
import hashlib
import json
import logging
import pathlib
import typing

from rag import models
from rag.config import ChunkingConfig
from rag.pipelines.chunk.stages.validator import ValidationMetrics

logger = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class ChunkingManifest:
    config: ChunkingConfig

    def create(
        self,
        documents: list[models.PreparedDocument],
        chunks: list[models.Chunk],
        validation_metrics: ValidationMetrics,
    ) -> dict[str, typing.Any]:
        run_id: typing.Final = self._build_run_id(
            documents=documents,
            chunks=chunks,
        )

        manifest: typing.Final[dict[str, typing.Any]] = {
            "run_id": run_id,
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "counts": {
                "documents": len(documents),
                "chunks": len(chunks),
            },
            "validation": dataclasses.asdict(validation_metrics),
            "config": {
                "strategy": self.config.strategy,
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
            },
        }

        logger.info(
            "Manifest created: run_id=%s, documents=%d, chunks=%d",
            run_id,
            len(documents),
            len(chunks),
        )

        return manifest

    def save(
        self,
        manifest: dict[str, typing.Any],
        output_dir: pathlib.Path,
    ) -> pathlib.Path:
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path: typing.Final = output_dir / "manifest.json"

        output_path.write_text(
            json.dumps(
                manifest,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        logger.info("Manifest exported: %s", output_path)

        return output_path

    def _build_run_id(
        self,
        documents: list[models.PreparedDocument],
        chunks: list[models.Chunk],
    ) -> str:
        payload: typing.Final = {
            "document_ids": [document.metadata.document_id for document in documents],
            "chunk_ids": [chunk.id for chunk in chunks],
            "strategy": self.config.strategy,
            "chunk_size": self.config.chunk_size,
            "chunk_overlap": self.config.chunk_overlap,
        }

        serialized: typing.Final = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")

        return hashlib.sha256(serialized).hexdigest()

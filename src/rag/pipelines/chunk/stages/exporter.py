import dataclasses
import json
import logging
import typing
from pathlib import Path

from rag import models

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class ChunkExporter:
    output_dir: Path

    def export(self, chunks: list[models.Chunk]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._export_json(chunks)
        self._export_jsonl(chunks)

        LOGGER_OBJ.info(
            "Exported %d chunks to %s",
            len(chunks),
            self.output_dir,
        )

    def _export_json(self, chunks: list[models.Chunk]) -> None:
        output_path: typing.Final = self.output_dir / "chunks.json"

        data: typing.Final = [chunk.model_dump(mode="json") for chunk in chunks]

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

    def _export_jsonl(self, chunks: list[models.Chunk]) -> None:
        output_path: typing.Final = self.output_dir / "chunks.jsonl"

        with output_path.open("w", encoding="utf-8") as file:
            for chunk in chunks:
                json.dump(
                    chunk.model_dump(mode="json"),
                    file,
                    ensure_ascii=False,
                )
                file.write("\n")

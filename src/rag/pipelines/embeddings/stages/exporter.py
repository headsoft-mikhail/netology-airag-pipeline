import dataclasses
import json
import typing
from pathlib import Path

from rag import models


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class EmbeddingExporter:
    output_dir: Path

    def export(self, embeddings: list[models.EmbeddedChunk]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._export_json(embeddings)
        self._export_jsonl(embeddings)

    def _export_json(self, embeddings: list[models.EmbeddedChunk]) -> None:
        output_path: typing.Final = self.output_dir / "embeddings.json"
        data: typing.Final = [one_embedding.model_dump(mode="json") for one_embedding in embeddings]

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

    def _export_jsonl(self, embeddings: list[models.EmbeddedChunk]) -> None:
        output_path: typing.Final = self.output_dir / "embeddings.jsonl"

        with output_path.open("w", encoding="utf-8") as file:
            for one_embedding in embeddings:
                json.dump(
                    one_embedding.model_dump(mode="json"),
                    file,
                    ensure_ascii=False,
                )
                file.write("\n")

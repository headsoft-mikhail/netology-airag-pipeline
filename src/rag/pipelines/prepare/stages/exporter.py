import json
import typing
from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True, slots=True, frozen=True)
class DatasetExporter:
    output_dir: Path

    def export(self, documents: list[dict]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._export_json(documents)
        self._export_jsonl(documents)

    def _export_json(self, documents: list[dict]) -> None:
        output_path: typing.Final = self.output_dir / "dataset.json"

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(documents, file, ensure_ascii=False, indent=2)

    def _export_jsonl(self, documents: list[dict]) -> None:
        output_path: typing.Final = self.output_dir / "dataset.jsonl"

        with output_path.open("w", encoding="utf-8") as file:
            for document in documents:
                file.write(json.dumps(document, ensure_ascii=False) + "\n")

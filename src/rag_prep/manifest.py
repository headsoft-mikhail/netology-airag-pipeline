import json
import typing
from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True, slots=True, frozen=True)
class Manifest:
    started_at: str
    input_documents: int
    output_documents: int
    exact_duplicates: int
    near_duplicates: int

    def save(self, output_path: Path) -> None:
        data: typing.Final = {
            "started_at": self.started_at,
            "input_documents": self.input_documents,
            "output_documents": self.output_documents,
            "exact_duplicates": self.exact_duplicates,
            "near_duplicates": self.near_duplicates,
        }

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

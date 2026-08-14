import dataclasses
import json
import typing
from pathlib import Path

from rag.pipelines.vector_store.stages.search import VectorSearchResult


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class VectorStoreExporter:
    output_dir: Path

    def export(self, search_results: list[VectorSearchResult]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        output_path: typing.Final = self.output_dir / "search_results.json"

        data: typing.Final = [dataclasses.asdict(one_search_result) for one_search_result in search_results]

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

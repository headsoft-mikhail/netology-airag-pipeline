import dataclasses
import logging
import typing

from qdrant_client.conversions.common_types import ScoredPoint

from evaluation.config import ContextBuilderConfig

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class ContextBuilder:
    config: ContextBuilderConfig

    def build_context(self, retrieval_results: list[ScoredPoint]) -> str:
        chunks: typing.Final[list[str]] = []
        context_logging_message = "Chunks used for context:"

        for index, point in enumerate(retrieval_results, start=1):
            if point.score < self.config.min_score:
                continue

            payload: dict[str, typing.Any] = point.payload or {}

            chunks.append(
                "\n".join(
                    [
                        f"[Фрагмент {index}]",
                        f"Источник: {payload.get('source')}",
                        f"Текст: {payload.get('text')}",
                    ]
                )
            )
            context_logging_message += f"\n{payload.get('chunk_id')}\tSource: {payload.get('source')}"
        LOGGER_OBJ.info(context_logging_message)

        return "\n\n".join(chunks)

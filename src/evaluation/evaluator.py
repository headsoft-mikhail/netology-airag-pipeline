import json
import logging
import typing

from evaluation.config import EvaluatorConfig
from evaluation.llm_client import LLMClient
from evaluation.retrieval_client import RetrievalClient

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


class Evaluator:
    def __init__(
        self,
        config: EvaluatorConfig,
    ) -> None:
        self.config = config

        self.retrieval_client = RetrievalClient(config=self.config.retrieval)
        self.llm_client = LLMClient(config=self.config.llm)

    def evaluate(self, query: str) -> str:
        retrieval_results: typing.Final = self.retrieval_client.top_k(query)
        LOGGER_OBJ.info("Retrieval - DONE!\n-------------")
        answer: typing.Final = self.llm_client.request(query=query, context=self._build_context(retrieval_results))
        LOGGER_OBJ.info(f"LLM request - DONE! Answer:\n {answer}\n-------------")
        return answer

    def test(self):
        LOGGER_OBJ.info("Run self-test")
        test_results: typing.Final = []
        for one_test_query in self.config.test.questions:
            retrieval_results = self.retrieval_client.top_k(one_test_query)
            answer = self.evaluate(one_test_query)
            test_results.append(
                {
                    "query": one_test_query,
                    "answer": answer,
                    "top_k": [one_result.model_dump() for one_result in retrieval_results],
                }
            )
        self._export_evaluation_data(test_results)

    def _export_evaluation_data(self, data):
        self.config.test.report_path.mkdir(parents=True, exist_ok=True)
        output_path: typing.Final = self.config.test.report_path / "evaluation_test.json"

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    @staticmethod
    def _build_context(retrieval_results: list[typing.Any]) -> str:
        chunks: typing.Final[list[str]] = []
        context_logging_message = "Chunks used for context:"

        for index, point in enumerate(retrieval_results, start=1):
            payload = point.payload if hasattr(point, "payload") and point.payload else {}

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

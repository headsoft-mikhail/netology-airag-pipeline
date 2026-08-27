import json
import logging
import time
import typing

from evaluation.config import EvaluatorConfig
from evaluation.context_builder import ContextBuilder
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
        self.context_builder = ContextBuilder(config=self.config.context)
        self.llm_client = LLMClient(config=self.config.llm)

    def evaluate(self, query: str) -> str:
        retrieval_results: typing.Final = self.retrieval_client.top_k(query)
        LOGGER_OBJ.info("Retrieval - DONE!\n-------------")
        context: typing.Final = self.context_builder.build_context(retrieval_results)
        return self._evaluate(query=query, context=context)

    def test(self) -> None:
        LOGGER_OBJ.info("Run self-test")
        test_results: typing.Final = []
        for one_test_query in self.config.test.questions:
            retrieval_results = self.retrieval_client.top_k(one_test_query)
            LOGGER_OBJ.info("Retrieval - DONE!\n-------------")
            time.sleep(1)
            context = self.context_builder.build_context(retrieval_results)
            answer = self._evaluate(query=one_test_query, context=context)
            test_results.append(
                {
                    "query": one_test_query,
                    "top_k": [one_result.model_dump() for one_result in retrieval_results],
                    "min_score": self.config.context.min_score,
                    "context": context,
                    "answer": answer,
                }
            )
        self._export_evaluation_data(test_results)

    def _evaluate(self, query: str, context: str) -> str:
        answer: typing.Final = self.llm_client.request(query=query, context=context)
        LOGGER_OBJ.info(f"LLM request - DONE! Answer:\n {answer}\n-------------")
        return answer

    def _export_evaluation_data(self, data: list[dict[str, typing.Any]]) -> None:
        self.config.test.report_path.mkdir(parents=True, exist_ok=True)
        output_path: typing.Final = self.config.test.report_path / "evaluation_test.json"

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

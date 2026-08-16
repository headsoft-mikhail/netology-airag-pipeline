import os
import typing
from pathlib import Path

import pydantic
import yaml
from dotenv import load_dotenv


class LLMConfig(pydantic.BaseModel):
    url: str
    model: str

    @property
    def api_key(self):
        return os.environ["GROQ_API_KEY"]


class ContextBuilderConfig(pydantic.BaseModel):
    min_score: float


class RetrievalConfig(pydantic.BaseModel):
    embedding_model: str
    vector_store_path: str
    collection_name: str
    search_top_k: int
    excluded_documents: list[str]


class TestEvaluationConfig(pydantic.BaseModel):
    questions: list[str]
    report_path: Path


class EvaluatorConfig(pydantic.BaseModel):
    llm: LLMConfig
    context: ContextBuilderConfig
    retrieval: RetrievalConfig
    test: TestEvaluationConfig


def load_evaluator_config(path: Path) -> EvaluatorConfig:
    load_dotenv(".env")
    with path.open("r", encoding="utf-8") as file:
        data: typing.Final = yaml.safe_load(file)

    return EvaluatorConfig.model_validate(data)

import typing
from pathlib import Path

import pydantic
import yaml


class PathsConfig(pydantic.BaseModel):
    input: Path
    output: Path


class ParsingConfig(pydantic.BaseModel):
    supported_formats: list[str]


class CleaningConfig(pydantic.BaseModel):
    remove_empty_documents: bool = True


class NormalizationConfig(pydantic.BaseModel):
    unicode_form: typing.Literal["NFC", "NFD", "NFKC", "NFKD"] = "NFC"


class DeduplicationConfig(pydantic.BaseModel):
    exact: bool = True
    near_duplicate: bool = True
    similarity_threshold: float = 0.85


class ExportConfig(pydantic.BaseModel):
    json: bool = True
    jsonl: bool = True


class PipelineConfig(pydantic.BaseModel):
    paths: PathsConfig
    parsing: ParsingConfig
    cleaning: CleaningConfig
    normalization: NormalizationConfig
    deduplication: DeduplicationConfig
    export: ExportConfig


def load_config(path: Path) -> PipelineConfig:
    with path.open("r", encoding="utf-8") as file:
        data: typing.Final = yaml.safe_load(file)

    return PipelineConfig.model_validate(data)

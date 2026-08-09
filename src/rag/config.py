import typing
from pathlib import Path

import pydantic
import tiktoken
import yaml


class PathsConfig(pydantic.BaseModel):
    input: Path
    prepared: Path
    chunks: Path

    @property
    def prepared_jsonl(self):
        return Path(self.prepared, "dataset.jsonl")


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


class ChunkingConfig(pydantic.BaseModel):
    strategy: typing.Literal["sentence", "paragraph", "token", "text"]
    chunk_size: int = pydantic.Field(gt=0)
    chunk_overlap: int = pydantic.Field(ge=0)
    tokenizer_model: str

    @pydantic.model_validator(mode="after")
    def validate_overlap(self) -> typing.Self:
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return self

    @property
    def tokenizer(self):
        return tiktoken.encoding_for_model(self.tokenizer_model)


class PipelineConfig(pydantic.BaseModel):
    paths: PathsConfig
    parsing: ParsingConfig
    cleaning: CleaningConfig
    normalization: NormalizationConfig
    deduplication: DeduplicationConfig
    export: ExportConfig
    chunking: ChunkingConfig


def load_config(path: Path) -> PipelineConfig:
    with path.open("r", encoding="utf-8") as file:
        data: typing.Final = yaml.safe_load(file)

    return PipelineConfig.model_validate(data)

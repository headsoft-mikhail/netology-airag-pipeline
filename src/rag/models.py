import pydantic


class SourceDocument(pydantic.BaseModel):
    content: str
    source: str
    file_type: str


class ParsedDocument(pydantic.BaseModel):
    text: str
    source: str
    file_type: str
    sections: list[str] = pydantic.Field(default_factory=list)
    character_count: int = 0
    word_count: int = 0
    sentence_count: int = 0


class DeduplicationResult(pydantic.BaseModel):
    documents: list[ParsedDocument]
    exact_duplicates: int = 0
    near_duplicates: int = 0


class PreparedDocumentMetadata(pydantic.BaseModel):
    source: str
    file_type: str
    document_id: str
    section: list[str] = pydantic.Field(default_factory=list)
    character_count: int = 0
    word_count: int = 0
    sentence_count: int = 0


class PreparedDocument(pydantic.BaseModel):
    text: str
    metadata: PreparedDocumentMetadata
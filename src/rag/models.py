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


class ChunkMetadata(pydantic.BaseModel):
    document_id: str
    position: int
    chunk_token_count: int
    chunk_size: int
    chunk_overlap: int
    chunking_strategy: str
    source: str | None = None
    section: str | None = None
    text_hash: str


class Chunk(pydantic.BaseModel):
    id: str
    text: str
    metadata: ChunkMetadata


class EmbeddedChunkMetadata(ChunkMetadata):
    embedding_model: str
    embedding_dimensions: int


class EmbeddedChunk(pydantic.BaseModel):
    id: str
    text: str
    embedding: list[float]
    metadata: EmbeddedChunkMetadata

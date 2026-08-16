import typing

import qdrant_client
from qdrant_client.conversions.common_types import ScoredPoint
from qdrant_client.models import FieldCondition, Filter, MatchValue
from sentence_transformers import SentenceTransformer

from evaluation.config import RetrievalConfig


class RetrievalClient:
    def __init__(self, config: RetrievalConfig) -> None:
        self.config = config
        self.transformer = SentenceTransformer(self.config.embedding_model)

    def top_k(self, query: str) -> list[ScoredPoint]:
        query_embedding: typing.Final = self.transformer.encode(query).tolist()

        vector_store_client: typing.Final = qdrant_client.QdrantClient(path=str(self.config.vector_store_path))

        query_filter: typing.Final = Filter(
            must_not=[
                FieldCondition(key="source", match=MatchValue(value=one_document))
                for one_document in self.config.excluded_documents
            ],
        )
        return vector_store_client.query_points(
            collection_name=self.config.collection_name,
            query=query_embedding,
            query_filter=query_filter,
            limit=self.config.search_top_k,
            with_payload=True,
        ).points

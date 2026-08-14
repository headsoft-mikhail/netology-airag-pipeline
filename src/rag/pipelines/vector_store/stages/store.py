import dataclasses
import logging
import typing
import uuid

import qdrant_client
from qdrant_client import models as qdrant_models

from rag import models as rag_models
from rag.config import VectorStoreConfig

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class QdrantStore:
    config: VectorStoreConfig
    client: qdrant_client.QdrantClient

    def create_collection(self) -> None:
        collection_name: typing.Final = self.config.collection_name

        if self.client.collection_exists(collection_name):
            if self.config.recreate_collection:
                LOGGER_OBJ.info(f"Collection {collection_name} already exists. Recreating...")
                self.client.delete_collection(collection_name)
            else:
                LOGGER_OBJ.info(f"Collection {collection_name} already exists. Using existing collection.")
                return

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=self.config.vectors_dimensions,
                distance=self._get_distance(),
            ),
        )

        LOGGER_OBJ.info(f"Collection {collection_name} created.")

    def upload(self, embedded_chunks: list[rag_models.EmbeddedChunk]) -> int:
        total_uploaded = 0

        for start in range(0, len(embedded_chunks), self.config.upload_batch_size):
            batch = embedded_chunks[start : start + self.config.upload_batch_size]
            points = [
                qdrant_models.PointStruct(
                    id=uuid.uuid5(uuid.NAMESPACE_URL, one_embedded_chunk.id),
                    vector=one_embedded_chunk.embedding,
                    payload={
                        "chunk_id": one_embedded_chunk.id,
                        "text": one_embedded_chunk.text,
                        **one_embedded_chunk.metadata.model_dump(),
                    },
                )
                for one_embedded_chunk in batch
            ]

            self.client.upsert(
                collection_name=self.config.collection_name,
                points=points,
                wait=True,
            )
            total_uploaded += len(points)
            LOGGER_OBJ.info(f"Uploaded {total_uploaded}/{len(embedded_chunks)} embeddings.")

        return total_uploaded

    def get_all_points(self, limit: int = 10_000) -> list[qdrant_models.Record]:
        return self.client.scroll(
            collection_name=self.config.collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=True,
        )[0]

    def _get_distance(self) -> qdrant_models.Distance:
        distances: typing.Final = {
            "cosine": qdrant_models.Distance.COSINE,
            "dot": qdrant_models.Distance.DOT,
            "euclid": qdrant_models.Distance.EUCLID,
            "manhattan": qdrant_models.Distance.MANHATTAN,
        }

        return distances[self.config.distance]

    def close(self) -> None:
        self.client.close()

from abc import ABC, abstractmethod

from rag_engine.models import DocumentChunk, EvidenceResult, RetrievalQuery


class DocumentIngestor(ABC):
    @abstractmethod
    def ingest(self, raw_text: str, metadata: dict[str, object]) -> list[DocumentChunk]:
        raise NotImplementedError


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class VectorStore(ABC):
    @abstractmethod
    def add_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(self, query_embedding: list[float], query: RetrievalQuery) -> list[EvidenceResult]:
        raise NotImplementedError


class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: RetrievalQuery) -> list[EvidenceResult]:
        raise NotImplementedError


class Reranker(ABC):
    @abstractmethod
    def rerank(self, query: RetrievalQuery, results: list[EvidenceResult]) -> list[EvidenceResult]:
        raise NotImplementedError


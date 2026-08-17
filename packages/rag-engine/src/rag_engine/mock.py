from rag_engine.interfaces import Retriever
from rag_engine.models import Citation, DocumentChunk, EvidenceResult, RetrievalQuery


class InMemoryRetriever(Retriever):
    def __init__(self, chunks: list[DocumentChunk] | None = None) -> None:
        self._chunks = chunks or []

    def add(self, chunk: DocumentChunk) -> None:
        self._chunks.append(chunk)

    def retrieve(self, query: RetrievalQuery) -> list[EvidenceResult]:
        results: list[EvidenceResult] = []
        query_terms = set(query.question.lower().split()) | {tag.lower() for tag in query.tags}

        for chunk in self._chunks:
            if chunk.metadata.terminal_id != query.terminal_id:
                continue
            if query.subsystem and chunk.metadata.subsystem != query.subsystem:
                continue
            if query.entity_ids and chunk.metadata.entity_id not in query.entity_ids:
                continue

            chunk_terms = set(chunk.text.lower().split()) | {
                tag.lower() for tag in chunk.metadata.tags
            }
            overlap = len(query_terms & chunk_terms)
            if overlap == 0 and query.tags:
                continue
            score = min(1.0, 0.2 + overlap / 10)
            results.append(
                EvidenceResult(
                    citation=Citation(
                        document_id=chunk.document_id,
                        chunk_id=chunk.chunk_id,
                        score=score,
                    ),
                    text=chunk.text,
                    metadata=chunk.metadata,
                )
            )

        return sorted(results, key=lambda result: result.citation.score, reverse=True)[
            : query.limit
        ]

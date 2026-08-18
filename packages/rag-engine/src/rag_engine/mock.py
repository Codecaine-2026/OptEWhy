from rag_engine.interfaces import Retriever
from rag_engine.models import Citation, DocumentChunk, EvidenceResult, RetrievalQuery


class InMemoryRetriever(Retriever):
    def __init__(self, chunks: list[DocumentChunk] | None = None) -> None:
        self._chunks = chunks or []

    def add(self, chunk: DocumentChunk) -> None:
        self._chunks.append(chunk)

    def retrieve(self, query: RetrievalQuery) -> list[EvidenceResult]:
        results: list[EvidenceResult] = []
        query_terms = _terms(query.question) | {tag.lower() for tag in query.tags}

        for chunk in self._chunks:
            if chunk.metadata.terminal_id != query.terminal_id:
                continue
            if query.subsystem and chunk.metadata.subsystem != query.subsystem:
                continue
            searchable_entity_ids = {
                value
                for value in [
                    chunk.metadata.entity_id,
                    *chunk.metadata.related_nodes,
                    *chunk.metadata.scenario_ids,
                ]
                if value
            }
            if query.entity_ids and not searchable_entity_ids.intersection(query.entity_ids):
                continue

            chunk_terms = (
                _terms(chunk.text)
                | {tag.lower() for tag in chunk.metadata.tags}
                | {node_id.lower() for node_id in chunk.metadata.related_nodes}
                | {scenario_id.lower() for scenario_id in chunk.metadata.scenario_ids}
            )
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


def _terms(text: str) -> set[str]:
    normalized = "".join(character.lower() if character.isalnum() else " " for character in text)
    return {term for term in normalized.split() if term}

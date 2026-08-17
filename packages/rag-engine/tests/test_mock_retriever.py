from rag_engine.mock import InMemoryRetriever
from rag_engine.models import DocumentChunk, DocumentMetadata, RetrievalQuery


def test_retriever_filters_by_metadata() -> None:
    retriever = InMemoryRetriever(
        [
            DocumentChunk(
                chunk_id="chunk_1",
                document_id="doc_1",
                text="QC4 hydraulic alarm reduced availability during the shift.",
                metadata=DocumentMetadata(
                    document_id="doc_1",
                    document_type="maintenance_report",
                    terminal_id="terminal_alpha",
                    entity_type="equipment",
                    entity_id="qc4",
                    subsystem="quay",
                    tags=["qc4", "availability"],
                ),
            )
        ]
    )

    results = retriever.retrieve(
        RetrievalQuery(
            question="Why did QC4 availability drop?",
            terminal_id="terminal_alpha",
            entity_ids=["qc4"],
            subsystem="quay",
        )
    )

    assert len(results) == 1
    assert results[0].citation.document_id == "doc_1"


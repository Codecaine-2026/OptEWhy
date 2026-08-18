import json
from pathlib import Path

from rag_engine.mock import InMemoryRetriever
from rag_engine.models import DocumentChunk, DocumentMetadata, RetrievalQuery

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SEED_PATH = REPOSITORY_ROOT / "data/rag/port_structural_causality_seed.jsonl"


def _load_seed_chunks() -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    with SEED_PATH.open(encoding="utf-8") as seed_file:
        for line in seed_file:
            payload = json.loads(line)
            chunks.append(
                DocumentChunk(
                    chunk_id=payload["chunk_id"],
                    document_id=payload["document_id"],
                    text=payload["text"],
                    metadata=DocumentMetadata(
                        document_id=payload["document_id"],
                        document_type=payload["document_type"],
                        terminal_id=payload["terminal_id"],
                        source_title=payload.get("source_title"),
                        source_url=payload.get("source_url"),
                        publisher=payload.get("publisher"),
                        published_date=payload.get("published_date"),
                        evidence_scope=payload.get("evidence_scope"),
                        claim_type=payload.get("claim_type"),
                        subsystem=payload.get("subsystem"),
                        tags=payload.get("tags", []),
                        related_nodes=payload.get("related_nodes", []),
                        related_edges=payload.get("related_edges", []),
                        scenario_ids=payload.get("scenario_ids", []),
                    ),
                )
            )
    return chunks


def test_rag_seed_chunks_validate_against_model() -> None:
    chunks = _load_seed_chunks()

    assert len(chunks) == 7
    assert all(chunk.metadata.source_url for chunk in chunks)
    assert any("qc_productivity" in chunk.metadata.related_nodes for chunk in chunks)


def test_seed_retriever_returns_relevant_structural_evidence() -> None:
    retriever = InMemoryRetriever(_load_seed_chunks())

    qc_results = retriever.retrieve(
        RetrievalQuery(
            question="Why is QC productivity down?",
            terminal_id="terminal_alpha",
            entity_ids=["qc_productivity"],
        )
    )
    chassis_results = retriever.retrieve(
        RetrievalQuery(
            question="Could chassis shortage cause yard congestion?",
            terminal_id="terminal_alpha",
            entity_ids=["chassis_availability"],
        )
    )
    truck_results = retriever.retrieve(
        RetrievalQuery(
            question="Why is truck turn time high if gate lanes are not the root cause?",
            terminal_id="terminal_alpha",
            entity_ids=["truck_turn_time"],
        )
    )

    assert qc_results
    assert chassis_results
    assert truck_results
    assert chassis_results[0].citation.document_id == "industry_chassis_dwell_yard_density"
    assert any("yard retrieval" in result.text.lower() for result in truck_results)

import json
from functools import lru_cache
from pathlib import Path

from rag_engine.models import DocumentChunk, DocumentMetadata

REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_SEED_PATH = REPOSITORY_ROOT / "data/rag/port_structural_causality_seed.jsonl"


@lru_cache(maxsize=1)
def load_rag_seed_chunks(path: str = str(DEFAULT_SEED_PATH)) -> tuple[DocumentChunk, ...]:
    chunks: list[DocumentChunk] = []
    with Path(path).open(encoding="utf-8") as seed_file:
        for line in seed_file:
            if not line.strip():
                continue
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
    return tuple(chunks)

import argparse
import json
from pathlib import Path

from rag_engine.models import DocumentChunk, DocumentMetadata

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPOSITORY_ROOT / "data/rag/port_structural_causality_seed.jsonl"


def load_seed_chunks(path: Path = DEFAULT_INPUT) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    with path.open(encoding="utf-8") as seed_file:
        for line_number, line in enumerate(seed_file, start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            chunk = DocumentChunk(
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
            if chunk.document_id != chunk.metadata.document_id:
                raise ValueError(f"Document ID mismatch on line {line_number}")
            chunks.append(chunk)
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and load RAG seed chunks.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()

    chunks = load_seed_chunks(args.input)
    print(f"Loaded {len(chunks)} RAG seed chunks from {_display_path(args.input)}")


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPOSITORY_ROOT))
    except ValueError:
        return str(resolved)


if __name__ == "__main__":
    main()

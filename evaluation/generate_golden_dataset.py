import sys
import json
import re
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import anthropic
from src.ingestion.loaders import DocumentLoader
from src.ingestion.chunker import RecursiveChunker
from config.settings import settings


def generate_triplets_from_docs(
    input_dir: Path,
    output_file: Path,
    api_key: str = settings.ANTHROPIC_API_KEY
) -> None:
    """Generate (Query, Context, Ground Truth) evaluation triplets from source documents."""
    print(f"[Dataset Gen] Loading documents from: {input_dir}")
    pages = DocumentLoader.load_directory(input_dir)
    chunker = RecursiveChunker(chunk_size=400, chunk_overlap=50)
    chunks = chunker.chunk_pages(pages)

    print(f"[Dataset Gen] Extracted {len(chunks)} chunks across {len(pages)} pages.")

    client = None
    if api_key and api_key != "mock-key":
        try:
            client = anthropic.Anthropic(api_key=api_key)
        except Exception:
            client = None

    dataset: List[Dict[str, Any]] = []

    for idx, chunk in enumerate(chunks):
        if len(chunk.content.strip()) < 80:
            continue

        if client:
            prompt = f"""You are an automated evaluation dataset generator for an Enterprise RAG test suite.
Given the following enterprise document snippet, generate:
1. A realistic, specific user query that can ONLY be answered using this snippet.
2. The ground truth answer directly supported by the text.

Document Name: {chunk.doc_name} (Page {chunk.page_number})
Snippet:
{chunk.content}

Return ONLY valid JSON in this exact schema:
{{
  "query": "Realistic user question?",
  "ground_truth": "Concise factual answer with specific numbers/facts from text."
}}"""
            try:
                response = client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=400,
                    temperature=0.2,
                    system="You generate synthetic QA evaluation datasets. Output only JSON.",
                    messages=[{"role": "user", "content": prompt}]
                )
                match = re.search(r"\{.*\}", response.content[0].text, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    dataset.append({
                        "id": f"eval_{idx+1:03d}",
                        "query": data["query"],
                        "ground_truth": data["ground_truth"],
                        "target_doc": chunk.doc_name,
                        "target_page": chunk.page_number,
                        "context_reference": chunk.content,
                    })
                    print(f"  + Generated sample {len(dataset)}: {data['query'][:60]}...")
            except Exception as e:
                print(f"  - Error on chunk {idx}: {e}")
        else:
            # Deterministic fallback sample generator
            dataset.append({
                "id": f"eval_{idx+1:03d}",
                "query": f"What are the specifications described in {chunk.doc_name} regarding {chunk.content.split()[0:5]}?",
                "ground_truth": chunk.content[:200],
                "target_doc": chunk.doc_name,
                "target_page": chunk.page_number,
                "context_reference": chunk.content,
            })

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print(f"[Dataset Gen] Successfully wrote {len(dataset)} evaluation triplets to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic golden dataset for RAG evaluation.")
    parser.add_argument("--input-dir", type=Path, default=Path(__file__).parent / "sample_docs", help="Source docs dir")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "golden_dataset.json", help="Output JSON")
    args = parser.parse_args()

    generate_triplets_from_docs(args.input_dir, args.output)

"""Recursive text chunker preserving document and page metadata."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from src.ingestion.loaders import LoadedPage
from src.ingestion.hasher import generate_chunk_id
from config.settings import settings


class TextChunk(BaseModel):
    """Processed text chunk ready for vector and lexical indexing."""
    chunk_id: str
    content: str
    doc_name: str
    page_number: int
    char_start: int
    char_end: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RecursiveChunker:
    """Splits text recursively using structural delimiters with overlap."""

    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
        separators: List[str] | None = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", "? ", "! ", " ", ""]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text by separators until pieces fit in chunk_size."""
        final_chunks: List[str] = []
        if not text:
            return final_chunks

        # Find first valid separator present in text
        chosen_sep = ""
        for sep in separators:
            if sep == "":
                chosen_sep = ""
                break
            if sep in text:
                chosen_sep = sep
                break

        splits = text.split(chosen_sep) if chosen_sep else list(text)

        current_piece = []
        current_len = 0

        for split in splits:
            item = split if chosen_sep == "" else split + chosen_sep
            item_len = len(item)

            if current_len + item_len <= self.chunk_size:
                current_piece.append(item)
                current_len += item_len
            else:
                if current_piece:
                    combined = "".join(current_piece).strip()
                    if combined:
                        final_chunks.append(combined)
                    
                    # Compute overlap from previous piece
                    overlap_chars = 0
                    overlap_piece = []
                    for prev_item in reversed(current_piece):
                        if overlap_chars + len(prev_item) <= self.chunk_overlap:
                            overlap_piece.insert(0, prev_item)
                            overlap_chars += len(prev_item)
                        else:
                            break
                    current_piece = overlap_piece
                    current_len = overlap_chars

                # If single item exceeds chunk_size, recurse with finer separators
                if item_len > self.chunk_size:
                    next_seps = separators[separators.index(chosen_sep) + 1 :] if chosen_sep in separators else []
                    if next_seps:
                        sub_chunks = self._split_text(item, next_seps)
                        final_chunks.extend(sub_chunks)
                    else:
                        final_chunks.append(item[: self.chunk_size].strip())
                else:
                    current_piece.append(item)
                    current_len += item_len

        if current_piece:
            tail = "".join(current_piece).strip()
            if tail:
                final_chunks.append(tail)

        return [c for c in final_chunks if c]

    def chunk_pages(self, pages: List[LoadedPage]) -> List[TextChunk]:
        """Convert a list of LoadedPage objects into enriched TextChunk objects."""
        chunks: List[TextChunk] = []

        for page in pages:
            raw_text = page.text.strip()
            if not raw_text:
                continue

            raw_splits = self._split_text(raw_text, self.separators)
            cursor = 0

            for split_content in raw_splits:
                # Find start position
                start_pos = raw_text.find(split_content[:30], cursor) if len(split_content) >= 30 else raw_text.find(split_content, cursor)
                if start_pos == -1:
                    start_pos = cursor
                end_pos = start_pos + len(split_content)
                cursor = max(cursor, start_pos + 1)

                chunk_id = generate_chunk_id(page.doc_name, page.page_number, split_content)

                chunk_meta = dict(page.metadata)
                chunk_meta["chunk_length"] = len(split_content)

                chunks.append(
                    TextChunk(
                        chunk_id=chunk_id,
                        content=split_content,
                        doc_name=page.doc_name,
                        page_number=page.page_number,
                        char_start=start_pos,
                        char_end=end_pos,
                        metadata=chunk_meta,
                    )
                )

        return chunks

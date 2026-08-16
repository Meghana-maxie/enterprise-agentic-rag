"""Document loaders for Text, Markdown, and PDF files."""

from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import pypdf


class LoadedPage(BaseModel):
    """Represents a single extracted page or section from a document."""
    doc_name: str
    page_number: int
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentLoader:
    """Unified document loader supporting .txt, .md, and .pdf."""

    @staticmethod
    def load_file(file_path: str | Path) -> List[LoadedPage]:
        """Load a single document and return a list of extracted pages."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        suffix = path.suffix.lower()
        if suffix in [".txt", ".md"]:
            return DocumentLoader._load_text_file(path)
        elif suffix == ".pdf":
            return DocumentLoader._load_pdf_file(path)
        else:
            raise ValueError(f"Unsupported file format '{suffix}'. Supported: .txt, .md, .pdf")

    @staticmethod
    def _load_text_file(path: Path) -> List[LoadedPage]:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        return [
            LoadedPage(
                doc_name=path.name,
                page_number=1,
                text=content,
                metadata={"file_size": path.stat().st_size, "extension": path.suffix}
            )
        ]

    @staticmethod
    def _load_pdf_file(path: Path) -> List[LoadedPage]:
        pages: List[LoadedPage] = []
        reader = pypdf.PdfReader(str(path))

        for idx, page in enumerate(reader.pages):
            extracted = page.extract_text() or ""
            if extracted.strip():
                pages.append(
                    LoadedPage(
                        doc_name=path.name,
                        page_number=idx + 1,
                        text=extracted,
                        metadata={"total_pages": len(reader.pages), "extension": ".pdf"}
                    )
                )

        return pages

    @staticmethod
    def load_directory(dir_path: str | Path) -> List[LoadedPage]:
        """Load all supported documents in a directory."""
        directory = Path(dir_path)
        all_pages: List[LoadedPage] = []

        for p in directory.glob("*"):
            if p.is_file() and p.suffix.lower() in [".txt", ".md", ".pdf"]:
                all_pages.extend(DocumentLoader.load_file(p))

        return all_pages

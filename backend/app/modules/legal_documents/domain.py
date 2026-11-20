from dataclasses import dataclass
from datetime import date
from hashlib import sha256


@dataclass(frozen=True)
class StagedDocument:
    source_url: str
    retrieved_at: str
    original_bytes: bytes
    effective_from: date | None = None
    effective_to: date | None = None

    @property
    def checksum(self) -> str:
        return sha256(self.original_bytes).hexdigest()


def validate_document(document: StagedDocument) -> str | None:
    if not document.source_url.startswith(("https://", "http://")):
        return "INVALID_SOURCE_URL"
    if not document.retrieved_at:
        return "MISSING_RETRIEVAL_TIME"
    if not document.original_bytes:
        return "EMPTY_DOCUMENT"
    if (
        document.effective_from
        and document.effective_to
        and document.effective_to < document.effective_from
    ):
        return "INVALID_EFFECTIVE_RANGE"
    return None

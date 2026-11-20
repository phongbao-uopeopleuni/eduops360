from datetime import date

from app.modules.legal_documents.domain import StagedDocument, validate_document


def test_document_requires_https_source_retrieval_and_content():
    document = StagedDocument(
        source_url="https://example.gov.vn/document.pdf",
        retrieved_at="2026-11-20T10:00:00+07:00",
        original_bytes=b"%PDF-synthetic",
        effective_from=date(2026, 9, 1),
        effective_to=date(2027, 5, 31),
    )
    assert validate_document(document) is None
    assert len(document.checksum) == 64


def test_document_rejects_non_source_empty_and_invalid_range():
    assert (
        validate_document(StagedDocument("ftp://example", "2026-11-20", b"x"))
        == "INVALID_SOURCE_URL"
    )
    assert (
        validate_document(StagedDocument("https://example", "", b"x")) == "MISSING_RETRIEVAL_TIME"
    )
    assert (
        validate_document(
            StagedDocument(
                "https://example",
                "2026-11-20",
                b"x",
                date(2027, 1, 1),
                date(2026, 1, 1),
            )
        )
        == "INVALID_EFFECTIVE_RANGE"
    )

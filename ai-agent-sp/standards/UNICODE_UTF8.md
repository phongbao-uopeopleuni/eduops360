# EduOps 360 — Unicode, UTF-8 and Vietnamese locale standard (v1.2)

**Canonical rule:** UTF-8 end-to-end; use Unicode NFC for user-facing text where semantically appropriate. All AI agents must read this policy before modifying text serialization, database schemas, imports/exports, or reports. The single canonical policy lives here; no tool-specific copies.

## 1. Files and transports

| Surface | Policy |
|---|---|
| Source code, Markdown, SQL, JSON, YAML, HTML, CSS | UTF-8 **without** BOM |
| Standard API JSON and machine CSV | UTF-8 without BOM; API response uses JSON UTF-8 |
| CSV exported for Windows Excel double-click use | UTF-8 **with BOM** (`utf-8-sig`); use `csv` quoting and `newline=''` |
| CSV imported by EduOps | Accept UTF-8 with or without BOM (`utf-8-sig` strict). Unsupported legacy encodings must be quarantined for explicit conversion/confirmation |
| Database | PostgreSQL database + client encoding UTF8; never use SQL_ASCII |
| HTML / HTTP text | `<meta charset="utf-8">` and appropriate `Content-Type` / charset |
| Date fields / IDs | ISO `YYYY-MM-DD` for dates; IDs are text, preserve zeros (e.g. `00125`) |
| Server timestamps | timezone-aware UTC; display in configured school timezone |
| Logs | Structured UTF-8; never dump raw student records/secrets in error messages |
| PDF | Use fonts with Vietnamese glyph coverage and embed appropriate licensed fonts in generated document; verify text extraction |

**Do not treat BOM as a font or encoding fix:** BOM is a UTF-8 signature used by some software. For CSV read, `utf-8-sig` strips it if present. For machine-readable artifacts prefer UTF-8 without BOM.

## 2. Unicode normalization

- Normalize relevant text (e.g. full names, class labels, document titles) to NFC *after successful strict UTF-8 decode and validation*, before storing and indexing.
- Preserve original uploaded bytes separately only if needed for approved import audit, with access controls, retention and SHA-256 checksum. Do not auto-transform legal originals.
- Never strip Vietnamese diacritics from canonical student names. Use a separate derived search key or PostgreSQL `unaccent` for accent-insensitive search, and check Vietnamese `đ` handling.
- Avoid silent `errors='ignore'` and `errors='replace'`; report malformed input and its location.
- Do not automatically guess VNI/TCVN3/Windows-1258. Offer reviewed, explicit legacy-conversion workflow when needed.

## 3. CSV conventions

- Template header uses stable ASCII `snake_case` keys. Human-readable Vietnamese labels are shown in UI/docs.
- A template includes a version and documented column schema; never silently accept unexpected headers or reorder mappings without user confirmation.
- Validate delimiter, quoting, row length, file size, maximum rows, required columns, date types, referential IDs, duplicate identifiers and permission scope.
- Preflight → preview → explicit confirmation → transactional staging/commit → audit + error-report. Failed rows must not silently overwrite students.
- Spreadsheet may coerce long IDs, leading-zero IDs and dates even with BOM. Offer `.xlsx` with explicit Text cell formats as a user-friendly alternative.
- Formula injection: treat all user-controlled values in **exports** as untrusted. Distinguish human-oriented spreadsheet exports from machine CSV; protect cells capable of being interpreted as formulas. No universal escaping scheme works in every spreadsheet.
- Import should never evaluate spreadsheet formula text.

## 4. Web rendering and font coverage

- Set `lang="vi"` on Vietnamese pages and UTF-8 metadata near the beginning of `<head>`.
- Use a verified Unicode-capable primary font (e.g. Source Sans 3) and well-tested fallback chain. Confirm Vietnamese glyphs on Chrome/Edge/Firefox, Windows/Linux, Light/Dark.
- Do not assume web fonts can be reused or redistributed inside PDF artifacts without checking license and embedding permissions.
- PDF charts and reports must render, copy and extract names with diacritics correctly; verify on CI/integration tests where feasible.

## 5. Acceptance / fixtures

Test strings (synthetic only): `Nguyễn Thị Ánh`, `Đặng Hoàng Phúc`, `Trần Thị Hồng`, `Thừa Thiên Huế`, `Lịch sử và Địa lí`, `00125`.

- Strict UTF-8 source decode passes; only approved CSV templates contain BOM.
- Both UTF-8 and UTF-8-BOM sample CSV parse identically.
- NFC vs NFD spelling of same name yields canonical equivalence in normalized values.
- Export → import round-trip preserves Vietnamese text, `00125`, embedded comma, double quote and newline.
- UTF-16 or invalid UTF-8 is rejected with a structured import error (no silent corruption).
- A leading formula marker is never emitted as executable spreadsheet content in human-facing reports.
- PostgreSQL `SHOW server_encoding; SHOW client_encoding;` returns `UTF8` in the deployed connection.
- HTML / API / CSV / PDF verify Vietnamese text through actual rendering where applicable.

## 6. Reference documentation (retrieved 2026-11-12)

- Microsoft Excel UTF-8 CSV BOM: https://support.microsoft.com/en-us/excel/opening-csv-utf-8-files-correctly-in-excel
- Python csv: https://docs.python.org/3.13/library/csv.html
- Python codecs utf-8-sig: https://docs.python.org/3.13/library/codecs.html
- Unicode NFC: https://www.unicode.org/reports/tr15/
- PostgreSQL character encoding: https://www.postgresql.org/docs/current/multibyte.html
- PostgreSQL unaccent: https://www.postgresql.org/docs/current/unaccent.html
- OWASP CSV injection: https://owasp.org/www-community/attacks/CSV_Injection
- OWASP secure upload: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html

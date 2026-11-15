# ADR-0005 — Password Hashing with Argon2id

**Date:** 2026-11-12  
**Status:** Proposed (chưa có approver chỉ định theo OD-001)  
**Task:** EDU-0013

## Context

EduOps 360 cần lưu trữ mật khẩu người dùng một cách an toàn. Cần chọn thuật toán hashing phù hợp với các tiêu chuẩn bảo mật hiện đại.

## Decision

Sử dụng **Argon2id** thông qua package `argon2-cffi` với các tham số:
- time_cost: 3 (iterations)
- memory_cost: 65536 KB (64 MB)
- parallelism: 4
- hash_len: 32 bytes
- salt_len: 16 bytes

## Rationale

1. **OWASP recommendation:** Argon2id là thuật toán được OWASP khuyến nghị cho password hashing
2. **PHC winner:** Argon2 thắng Password Hashing Competition 2015
3. **Memory-hard:** Chống GPU/ASIC attacks hiệu quả hơn bcrypt/scrypt
4. **Argon2id hybrid:** Kết hợp ưu điểm của Argon2i (side-channel resistance) và Argon2d (GPU resistance)
5. **Python ecosystem:** `argon2-cffi` là implementation được maintain tốt, có bindings tới libargon2

## Alternatives considered

| Algorithm | Pros | Cons | Decision |
|-----------|------|------|----------|
| bcrypt | Battle-tested, simple | 72-char limit, less memory-hard | Rejected |
| scrypt | Memory-hard | Complex tuning, slower adoption | Rejected |
| PBKDF2 | FIPS compliant | Not memory-hard, weaker against GPU | Rejected |

## Implementation

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)

# Hash
hashed = ph.hash(password)

# Verify
try:
    ph.verify(hashed, password)
except VerifyMismatchError:
    # Wrong password
    pass
```

## Consequences

- Need to add `argon2-cffi` to dependencies
- Hash verification takes ~100ms with these parameters (intentional for security)
- Parameters may need adjustment based on server hardware
- Future: Consider rehashing on login if parameters change

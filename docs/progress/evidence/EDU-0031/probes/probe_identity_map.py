"""Probe: does a second ORM SELECT ... FOR UPDATE refresh an object already in the
identity map? `_consume_account_token` (backend/app/modules/auth/router.py:69-101)
relies on that to re-check `used_at` after acquiring the row lock.

Uses SQLite in-memory (FOR UPDATE is a no-op there; only ORM refresh behaviour is
observed). Run with backend/.venv python (SQLAlchemy 2.1.8). Synthetic data only.
"""
import sqlalchemy
from sqlalchemy import String, create_engine, insert, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    used_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


def main() -> None:
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(insert(Token).values(id=1, used_at=None))

    with Session(engine, expire_on_commit=False, autoflush=False) as session_b:
        first = session_b.execute(select(Token).where(Token.id == 1)).scalar_one()
        print("B first read used_at =", first.used_at)
        # Concurrent request A consumes the token (simulated as a direct UPDATE)
        session_b.connection().execute(
            update(Token).where(Token.id == 1).values(used_at="2026-11-14")
        )
        db_value = session_b.connection().execute(
            sqlalchemy.text("SELECT used_at FROM tokens WHERE id = 1")
        ).scalar_one()
        print("row value now in DB =", db_value)
        locked = session_b.execute(
            select(Token).where(Token.id == 1).with_for_update()
        ).scalar_one()
        print("B with_for_update re-read used_at =", locked.used_at, "| same object:",
              locked is first)
        fresh = session_b.execute(
            select(Token)
            .where(Token.id == 1)
            .with_for_update()
            .execution_options(populate_existing=True)
        ).scalar_one()
        print("B populate_existing re-read used_at =", fresh.used_at)
    print("sqlalchemy", sqlalchemy.__version__)


if __name__ == "__main__":
    main()

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Metadata root. Domain tables are introduced by their owning phase."""

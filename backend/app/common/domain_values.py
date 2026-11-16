"""Runtime checks for the scalar fields of frozen domain value records."""

from dataclasses import fields


def validate_scalar_fields(value: object) -> None:
    """Reject untyped values before they can be nested in an immutable projection.

    Only scalar-annotated dataclasses (including optional scalars) use this
    helper; collection ownership is validated by the enclosing projection.
    """
    for field in fields(value):
        if not isinstance(getattr(value, field.name), field.type):
            raise TypeError(f"{field.name} has an invalid domain value type")

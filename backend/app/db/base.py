"""
Database Base Configuration

Central SQLAlchemy declarative base.

All ORM models must inherit from Base.

Metadata is automatically collected here
and consumed by Alembic migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Central declarative base class.

    All SQLAlchemy ORM models inherit from this class.
    """

    pass


# Central metadata reference for Alembic
metadata = Base.metadata
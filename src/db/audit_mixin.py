from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import declared_attr


class AuditMixin:
    """
    AuditMixin adds created/updated timestamps and user references.
    """

    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            default=datetime.now(timezone.utc),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            default=datetime.now(timezone.utc),
            onupdate=datetime.now(timezone.utc),
            nullable=False,
        )

    @declared_attr
    def created_by_id(cls):
        return Column(
            Integer,
            ForeignKey("core__users.id", ondelete="SET NULL"),
            nullable=True,
        )

    @declared_attr
    def updated_by_id(cls):
        return Column(
            Integer,
            ForeignKey("core__users.id", ondelete="SET NULL"),
            nullable=True,
        )

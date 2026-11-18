
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Event(Base):
    """Database model representing a corporate event."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    event_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    location: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )


class Registration(Base):
    """Database model representing an employee event registration."""

    __tablename__ = "registrations"

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "employee_email",
            name="unique_employee_event"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False
    )

    employee_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    employee_email: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

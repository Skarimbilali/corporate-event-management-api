
"""Business logic and database operations for events and registrations."""

import logging

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, time, timedelta

from app import models, schemas

logger = logging.getLogger("app.services")


async def create_event(db: AsyncSession, event_data: schemas.EventCreate):
    """Create a new event and save it in the database."""
    new_event = models.Event(**event_data.model_dump())

    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    logger.info("Event created: event_id=%s", new_event.id)

    return new_event


async def get_events(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    title: str | None = None,
    event_date: date | None = None
):
    """Get events with pagination and optional filters."""

    query = select(models.Event)

    if title:
        query = query.where(
            models.Event.title.ilike(f"%{title}%")
        )

    if event_date:
        start = datetime.combine(event_date, time.min)
        end = start + timedelta(days=1)

        query = query.where(
            models.Event.event_date >= start,
            models.Event.event_date < end
        )

    query = (
        query.order_by(models.Event.id)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    events = result.scalars().all()

    logger.info(
        "Events fetched: count=%s skip=%s limit=%s",
        len(events), skip, limit
    )

    return events



async def get_event_by_id(db: AsyncSession, event_id: int):
    """Retrieve a single event using its ID."""
    result = await db.execute(
        select(models.Event).where(models.Event.id == event_id)
    )

    event = result.scalar_one_or_none()
    logger.debug("Event lookup: event_id=%s found=%s", event_id, event is not None)

    return event


async def update_event(
    db: AsyncSession,
    event_id: int,
    event_data: schemas.EventUpdate
):
    """Update an existing event with the provided data."""
    event = await get_event_by_id(db, event_id)

    if event is None:
        logger.warning("Event update skipped: event_id=%s not found", event_id)
        return None

    for key, value in event_data.model_dump().items():
        setattr(event, key, value)

    await db.commit()
    await db.refresh(event)
    logger.info("Event updated: event_id=%s", event_id)

    return event


async def delete_event(db: AsyncSession, event_id: int):
    """Delete an event only when no employee registrations exist."""
    # Lock the event row so a registration cannot be created between
    # checking its registrations and deleting it (PostgreSQL).
    result = await db.execute(
        select(models.Event)
        .where(models.Event.id == event_id)
        .with_for_update()
    )
    event = result.scalar_one_or_none()

    if event is None:
        logger.warning("Event deletion skipped: event_id=%s not found", event_id)
        return None

    # PostgreSQL protects the relationship with a foreign key.
    # Return a meaningful HTTP error instead of triggering a 500.
    result = await db.execute(
        select(models.Registration.id)
        .where(models.Registration.event_id == event_id)
        .limit(1)
    )
    if result.scalar_one_or_none() is not None:
        logger.warning(
            "Event deletion rejected: event_id=%s has active registrations",
            event_id,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete event because it has active registrations",
        )

    await db.delete(event)
    await db.commit()
    logger.info("Event deleted successfully: event_id=%s", event_id)
    return True


async def create_registration(
    db: AsyncSession,
    event_id: int,
    registration_data: schemas.RegistrationCreate
):
    """Register an employee after checking the event business rules."""

    # Check whether the event exists.
    # Lock the event row for the duration of registration. PostgreSQL
    # serializes concurrent registrations for the same event this way.
    result = await db.execute(
        select(models.Event).where(models.Event.id == event_id).with_for_update()
    )
    event = result.scalar_one_or_none()

    if event is None:
        logger.warning("Registration rejected: event_id=%s not found", event_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # Prevent duplicate employee registration.
    result = await db.execute(
        select(models.Registration).where(
            models.Registration.event_id == event_id,
            models.Registration.employee_email == registration_data.employee_email
        )
    )

    existing_registration = result.scalar_one_or_none()

    if existing_registration:
        logger.warning("Duplicate registration rejected: event_id=%s", event_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee already registered for this event"
        )

    # Check event capacity.
    result = await db.execute(
        select(func.count()).select_from(models.Registration).where(
            models.Registration.event_id == event_id
        )
    )

    registration_count = result.scalar_one()

    if registration_count >= event.capacity:
        logger.warning("Registration rejected: event_id=%s capacity reached", event_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event capacity is full"
        )

    # Create the registration.
    new_registration = models.Registration(
        event_id=event_id,
        **registration_data.model_dump()
    )

    db.add(new_registration)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        # Database unique constraint is the final guard for simultaneous
        # duplicate registrations. Preserve the documented 409 response.
        logger.warning("Duplicate registration constraint: event_id=%s", event_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee already registered for this event"
        ) from exc
    await db.refresh(new_registration)
    logger.info("Registration created: registration_id=%s event_id=%s", new_registration.id, event_id)

    return new_registration


async def get_event_registrations(db: AsyncSession, event_id: int):
    """Retrieve all registrations for a specific event."""

    event = await get_event_by_id(db, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    result = await db.execute(
        select(models.Registration).where(
            models.Registration.event_id == event_id
        )
    )

    registrations = result.scalars().all()
    logger.debug("Event registrations listed: event_id=%s count=%s", event_id, len(registrations))

    return registrations


async def delete_registration(db: AsyncSession, registration_id: int):
    """Delete an employee registration using its ID."""

    result = await db.execute(
        select(models.Registration).where(
            models.Registration.id == registration_id
        )
    )

    registration = result.scalar_one_or_none()

    if registration is None:
        logger.warning("Registration deletion rejected: registration_id=%s not found", registration_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    await db.delete(registration)
    await db.commit()
    logger.info("Registration deleted: registration_id=%s", registration_id)

    return True

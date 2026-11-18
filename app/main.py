
"""API routes for the Corporate Event Management system."""

import logging
from time import perf_counter

from datetime import date
from fastapi import Query


from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app import schemas, services
from app.db import get_db
from app.logging_config import configure_logging

configure_logging()
logger = logging.getLogger("app.main")


app = FastAPI(
    title="Corporate Event Management API",
    description="API for managing corporate events and employee registrations.",
    version="1.0.0"
)


@app.middleware("http")
async def log_http_requests(request: Request, call_next):
    """Log request methods, paths, response codes and elapsed time, without body data."""
    start_time = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled request error: method=%s path=%s duration_ms=%.2f",
            request.method, request.url.path, (perf_counter() - start_time) * 1000,
        )
        raise

    duration_ms = (perf_counter() - start_time) * 1000
    log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
    logger.log(
        log_level,
        "HTTP request: method=%s path=%s status=%s duration_ms=%.2f",
        request.method, request.url.path, response.status_code, duration_ms,
    )
    return response


@app.get(
    "/",
    tags=["Home"],
    response_model=dict[str, str]
)
def home():
    """Return a welcome message."""
    return {
        "message": "Corporate Event Management API is running"
    }


@app.get(
    "/db-check",
    tags=["Database"]
)
async def database_check(
    db: AsyncSession = Depends(get_db)
):
    """Verify database connectivity by executing a harmless SQL query."""
    await db.execute(text("SELECT 1"))
    return {
        "message": "Database session received successfully"
    }


@app.post(
    "/events",
    response_model=schemas.EventResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Events"]
)
async def create_event(
    event_data: schemas.EventCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new corporate event."""
    return await services.create_event(db, event_data)



@app.get(
    "/events",
    response_model=list[schemas.EventResponse],
    tags=["Events"]
)
async def get_events(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    title: str | None = None,
    date: date | None = None,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve events with pagination and filtering."""

    return await services.get_events(
        db=db,
        skip=skip,
        limit=limit,
        title=title,
        event_date=date
    )



@app.get(
    "/events/{event_id}",
    response_model=schemas.EventResponse,
    tags=["Events"]
)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a specific event by its ID."""
    event = await services.get_event_by_id(db, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return event


@app.put(
    "/events/{event_id}",
    response_model=schemas.EventResponse,
    tags=["Events"]
)
async def update_event(
    event_id: int,
    event_data: schemas.EventUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing corporate event."""
    event = await services.update_event(
        db,
        event_id,
        event_data
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return event


@app.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    tags=["Events"]
)
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an event if it has no active registrations."""
    deleted = await services.delete_event(db, event_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/events/{event_id}/registrations",
    response_model=schemas.RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Registrations"]
)
async def create_registration(
    event_id: int,
    registration_data: schemas.RegistrationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register an employee for a specific event."""
    return await services.create_registration(
        db,
        event_id,
        registration_data
    )


@app.get(
    "/events/{event_id}/registrations",
    response_model=list[schemas.RegistrationResponse],
    tags=["Registrations"]
)
async def get_event_registrations(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all registrations for a specific event."""
    return await services.get_event_registrations(db, event_id)


@app.delete(
    "/registrations/{registration_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    tags=["Registrations"]
)
async def delete_registration(
    registration_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an employee registration."""
    await services.delete_registration(db, registration_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

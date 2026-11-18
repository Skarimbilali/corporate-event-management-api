


from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from datetime import datetime, timezone


class EventCreate(BaseModel):
    """Schema for validating new event data."""

    title: str = Field(min_length=1)
    description: str
    event_date: datetime
    location: str
    capacity: int = Field(gt=0)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        """Reject whitespace-only titles without changing valid title text."""
        if not value.strip():
            raise ValueError("Event title cannot be empty or whitespace")
        return value



    @field_validator("event_date")
    @classmethod
    def normalize_event_date(cls, value: datetime) -> datetime:
        """Convert timezone-aware dates to naive UTC for PostgreSQL."""

        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)

        return value


class EventUpdate(EventCreate):
    """Schema for validating event update data."""
    pass


class EventResponse(BaseModel):
    """Schema for returning event information."""

    id: int
    title: str
    description: str
    event_date: datetime
    location: str
    capacity: int

    model_config = ConfigDict(from_attributes=True)


class RegistrationCreate(BaseModel):
    """Schema for validating employee registration data."""

    employee_name: str = Field(min_length=1)
    employee_email: EmailStr

    @field_validator("employee_name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        """Reject employee names containing only whitespace."""
        if not value.strip():
            raise ValueError("Employee name cannot be empty or whitespace")
        return value


class RegistrationResponse(BaseModel):
    """Schema for returning registration information."""

    id: int
    event_id: int
    employee_name: str
    employee_email: EmailStr

    model_config = ConfigDict(from_attributes=True)

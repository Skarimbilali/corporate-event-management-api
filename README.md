# Corporate Event Management API

A RESTful API built with FastAPI and PostgreSQL to manage corporate events and employee registrations.

## Project Overview

The Corporate Event Management API allows users to create, retrieve, update, and delete corporate events. Employees can register for events, view registrations, and cancel their registrations.

The application uses asynchronous database operations with SQLAlchemy 2.0 and PostgreSQL.

## Features

- Create, retrieve, update, and delete events
- Register employees for events
- Retrieve event registrations
- Cancel employee registrations
- Prevent duplicate employee registrations
- Enforce event capacity limits
- Validate request data using Pydantic
- Return appropriate HTTP status codes

## Technologies Used

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Pydantic
- AsyncPG
- Uvicorn

## Project Structure

```text
corporate-event-management-api/
│
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── services.py
│
├── tests/
├── create_tables.py
├── test_db.py
├── requirements.txt
├── README.md
├── AI_USAGE.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd corporate-event-management-api
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure PostgreSQL

Create a PostgreSQL database named:

```text
corporate_event_db
```

Configure the database connection in `app/db.py`.

Set the `DB_PASSWORD` environment variable in PowerShell:

```powershell
$env:DB_PASSWORD = "YOUR_POSTGRES_PASSWORD"
```

Do not commit database passwords or other secrets to GitHub.

### 6. Create Database Tables

```bash
python create_tables.py
```

This creates the required `events` and `registrations` tables.

### 7. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

Open FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Events

| Method | Endpoint | Description |
|---|---|---|
| POST | `/events` | Create an event |
| GET | `/events` | Retrieve all events |
| GET | `/events/{event_id}` | Retrieve an event |
| PUT | `/events/{event_id}` | Update an event |
| DELETE | `/events/{event_id}` | Delete an event |

### Registrations

| Method | Endpoint | Description |
|---|---|---|
| POST | `/events/{event_id}/registrations` | Register an employee |
| GET | `/events/{event_id}/registrations` | Retrieve event registrations |
| DELETE | `/registrations/{registration_id}` | Delete a registration |

## Business Rules and Validations

- Event title must not be empty.
- Event capacity must be greater than zero.
- Required event fields must be provided.
- Employee email must be valid.
- An employee cannot register twice for the same event.
- Registration is not allowed for a non-existing event.
- Registration is rejected when event capacity is full.

## Event Deletion and Data Integrity

PostgreSQL foreign keys protect the relationship between events and registrations.
To avoid deleting attendee records unintentionally, `DELETE /events/{event_id}`
rejects an event with active registrations using `409 Conflict` and the message
`Cannot delete event because it has active registrations`. Cancel each associated
registration using `DELETE /registrations/{registration_id}` first, then delete
its event (`204 No Content`). An unknown event returns `404 Not Found`.
The foreign key constraint remains unchanged.

## HTTP Status Codes

| Status Code | Description |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 204 | Resource deleted successfully |
| 404 | Resource not found |
| 409 | Conflict, duplicate registration or full capacity |
| 422 | Request validation error |

## Testing

The API endpoints and business validations were manually tested using FastAPI Swagger UI.

Tested scenarios include event creation, retrieval, updating, deletion, duplicate registration prevention, capacity validation, and invalid input handling.

## AI Usage Documentation

Details about AI assistance used during development are documented in [AI_USAGE.md](AI_USAGE.md).

## Author

Sajid Karim

## License

This project was developed as part of an educational assignment.

## Pagination and Search (Bonus)

`GET /events` supports `skip` (default `0`, minimum `0`), `limit` (default `10`, range `1`–`100`), optional `title` (case-insensitive substring), and optional `date` (`YYYY-MM-DD`).

Examples:

```text
GET /events?skip=0&limit=10
GET /events?skip=10&limit=10
GET /events?title=Python
GET /events?date=2026-11-20
GET /events?title=Python&date=2026-11-20&skip=0&limit=5
```

Events are sorted by ID before applying offset/limit. A `422` response is expected for invalid query values.

## Date and Timezone Handling

The API accepts ISO 8601 dates, including `Z` or timezone offsets. Incoming timezone-aware timestamps are normalized to **UTC without timezone information**, matching the existing PostgreSQL `TIMESTAMP WITHOUT TIME ZONE` column. For example, `2026-11-20T15:00:00+05:00` is stored as `2026-11-20 10:00:00`. Timezone-naive dates are kept unchanged and treated by convention as UTC. Existing stored rows are not migrated by this code.

## Automated API Testing (pytest)

All commands run from the project root, after activating your virtual environment.

```powershell
python -m pip install -r requirements.txt
python -m pytest tests -v
```

To save test execution evidence:

```powershell
python -m pytest tests -v 2>&1 | Tee-Object -FilePath pytest-results.txt
```

`tests/test_api.py` covers event CRUD, registrations, business rules, `404`, `409`, `422`, logging and database health-check behavior. `tests/test_bonus_regression.py` covers pagination, title/date filtering, query validation, and UTC normalization.

**Test environment:** The automated tests use a fresh, disposable SQLite database through a test dependency override, not the production PostgreSQL database. Passing tests do not prove PostgreSQL connectivity or concurrency safety. The included `pytest-results.txt` is evidence of a previous local 30-test run; execute tests again after any changes to obtain current results.

## Manual PostgreSQL / Swagger Verification

1. Start your existing PostgreSQL 18 server and verify the `corporate_event_db` database exists. Use a dedicated test database if you plan to delete test events.
2. In **your own PowerShell terminal**, set `DB_PASSWORD` securely without sharing it or putting it in source code:

   ```powershell
   $env:DB_PASSWORD = Read-Host 'PostgreSQL password'
   ```

3. Run the database check: `python test_db.py`.
4. On a fresh database only, run `python create_tables.py` (existing tables are not dropped).
5. Start the API: `python -m uvicorn app.main:app --reload`.
6. Open `http://127.0.0.1:8000/docs`, test all eight required endpoints and save genuine screenshots displaying request URL, payload, response status and body.
7. Specifically test: missing event (`404`), duplicate registration (`409`), capacity full (`409`), invalid input (`422`), pagination and filtering. Make sure you also try timezone-offset event dates.
8. Separately test **two simultaneous registration requests for the last available seat** against PostgreSQL. Expected: at most one succeeds (`201`), one is rejected (`409`), and registrations never exceed capacity. This simultaneous-request behavior is **not** validated by the SQLite unit tests.

## Logging

Application logging is configured in `app/logging_config.py`. Uvicorn prints request logs and errors to the terminal. Set `LOG_LEVEL=DEBUG` in your PowerShell session if you need additional debug information. The existing SQLAlchemy `echo=True` setting in `app/db.py` was preserved.

## Git and Submission Checklist

The assignment requires a **public GitHub repository**, `main` stable branch, separate feature branches, meaningful commits, and completed work merged into `main`. These steps require your actual Git repository; a downloaded ZIP cannot demonstrate Git history.

Include the source files, this README, `requirements.txt`, `AI_USAGE.md`, screenshots of **real Swagger UI execution**, pytest evidence, and the mandatory demo video showing the running FastAPI service, PostgreSQL integration and all endpoints. A diagram-only narrated video does not substitute for a live demo. Share your actual AI prompts and chat history as required by the assignment. Frontend and JWT are optional bonus features; JWT is **not implemented** in this package.

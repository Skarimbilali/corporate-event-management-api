# AI Usage Documentation

**Project:** Corporate Event Management API  
**Technology stack:** Python 3.11, FastAPI, PostgreSQL, asynchronous SQLAlchemy, Pydantic, asyncpg, pytest  
**Assignment:** Corporate Event Management API (submission: 18 November 2026)  
**Project repository:** https://github.com/Skarimbilali/corporate-event-management-api

## 1. Purpose of AI Assistance

ChatGPT was used as a learning, coding, debugging, code-review, testing, and documentation assistant while developing the Corporate Event Management API. The developer remained responsible for deciding which suggestions to adopt, running the application, testing against PostgreSQL, and preparing the submission.

## 2. AI Tools, Model, and Configuration

| Item | Details |
|---|---|
| AI assistant | OpenAI ChatGPT |
| Model identified in this conversation | GPT-6 |
| Interaction | Conversational prompts, code snippets, uploaded source files, logs, and assignment PDF |
| Development environment reported by developer | Windows, Python 3.11, VS Code/PowerShell, PostgreSQL |
| AI-supported activities | Architecture guidance, API and validation logic, debugging, test design, documentation |

**Configuration disclosure:** No separate custom model parameters (such as temperature or top-p) were supplied in the visible project discussion. If additional AI tools or configurations were used outside this chat, disclose them separately. Database credentials and other secrets must not be included in the submitted conversation export.

## 3. Development Areas Assisted by AI

- FastAPI project separation: `db.py`, `models.py`, `schemas.py`, `services.py`, and `main.py`.
- Async PostgreSQL access using SQLAlchemy sessions and asyncpg.
- Event create, list, retrieve, update, and delete endpoints.
- Employee event registration, listing, and cancellation.
- Duplicate registration protection and capacity-limit validation.
- Pydantic validation, including whitespace-only input handling.
- Appropriate HTTP errors: `404 Not Found`, `409 Conflict`, and `422 Unprocessable Entity`.
- Pagination (`skip`, `limit`) and filtering by title/date.
- Request/service logging and database connectivity checks.
- Timezone-aware datetime conversion for PostgreSQL timestamp compatibility.
- Pytest coverage, Swagger testing instructions, README, and submission preparation.

## 4. Examples of Actual Project Requests and Prompt Topics

The following entries reflect requests made during the project conversation. Some are shortened for readability and **are not a replacement for the complete chat history**.

1. Review the existing Corporate Event Management API against the assignment PDF, preserving existing code and configuration.
2. Add logging without altering PostgreSQL settings or unrelated functionality.
3. Fix request validation for whitespace-only event titles and employee names.
4. Investigate PostgreSQL authentication and database connection failures.
5. Resolve the timezone-aware datetime insertion error with asyncpg.
6. Implement `skip`/`limit` pagination and search by title and event date.
7. Explain how to test endpoints and capture Swagger request/response evidence.
8. Add/run pytest tests for CRUD, registrations, duplicates, capacity, and errors.
9. Investigate `DELETE /events/2` returning `500 Internal Server Error`.
10. Review the PDF's deletion rules and preserve the database foreign key constraint.
11. Validate event deletion when active registrations exist, returning a useful `409 Conflict` rather than exposing an unhandled constraint failure.
12. Prepare/update the README, AI usage documentation, tests, and demonstration material.

## 5. Important Debugging Decisions

### PostgreSQL authentication

The API produced `asyncpg.exceptions.InvalidPasswordError` for database user `postgres`. The developer was instructed to verify the correct PostgreSQL instance and set the `DB_PASSWORD` environment variable in the same PowerShell session as Uvicorn. Credentials should not be committed or shared in documentation.

### Date/time handling

An asyncpg error occurred when a timezone-aware ISO datetime was passed to a PostgreSQL timestamp column without timezone support. A Pydantic normalization approach was discussed to convert aware values to UTC and remove `tzinfo` for storage consistent with the existing schema.

### Event deletion and foreign keys

PostgreSQL correctly rejected deleting an event referenced by registrations. The assignment requires an event DELETE endpoint but does not explicitly dictate cascading deletion. The selected application policy is to **retain referential integrity and prevent deletion while registrations exist**, returning `409 Conflict` with an explanatory message. Users may cancel registrations first; events with no registrations can be deleted, returning `204 No Content`. Nonexistent events should return `404 Not Found`.

This deletion policy is a project design decision, not a verbatim requirement from the assignment.

## 6. Testing and Verification Evidence

The developer supplied a real Windows pytest execution log from Python 3.11 showing **30 tests passed with one non-failing deprecation warning**. Further regression tests were added during subsequent project revisions. The developer was given the command to regenerate `pytest-results.txt`; the **current final count must be taken from that latest locally executed file**, rather than assuming earlier results describe the latest revision.

To regenerate the submission evidence in the project root:

```powershell
python -m pytest tests -v 2>&1 | Tee-Object -FilePath pytest-results.txt
```

Testing topics include:

- Successful event CRUD and registration operations.
- Validation errors, missing resources, duplicates, and capacity limits.
- Empty/whitespace values and database health checks.
- Pagination/date/title filtering (extended regression coverage).
- Deletion with active registrations, expecting `409 Conflict` (extended regression coverage).

**Evidence distinction:** Pytest tests use isolated test database fixtures; they do not by themselves prove production PostgreSQL connectivity or concurrent transaction behavior. Swagger screenshots were reported as captured by the developer; the actual screenshot files should accompany the submission. A successful `python test_db.py` run should also be verified locally.

## 7. Developer Contribution and Responsibility

The developer configured and operated PostgreSQL locally, ran Uvicorn and Swagger, supplied real logs/errors, made implementation choices, performed tests, and reviewed AI suggestions against the assignment PDF. AI responses and generated code were used as assistance and should be verified in the actual application before submission.

## 8. Conversation History and Submission Attachments

The assignment requests the **full relevant AI prompt and conversation history**, not just selected examples. Attach or export the genuine ChatGPT conversation(s) associated with this assignment, including debugging and changes, alongside `AI_USAGE.md`.

Before publishing, inspect the history and redact credentials, tokens, connection strings containing passwords, and any other secrets. Keep the history otherwise representative of the actual assistance received.

Recommended supporting evidence: `pytest-results.txt`, Swagger screenshots, README setup/testing instructions, source repository, and a live application demonstration recording.

## 9. Scope and Limitations

- JWT authentication was not implemented in the project version discussed here; it was intentionally deferred as an optional bonus.
- Frontend implementation is optional and was not required for the backend assignment.
- A narrated slide/diagram video is supplemental and should not be misrepresented as a live Swagger/PostgreSQL screen recording.
- This document records known assistance and verified information from the conversation; it is not a full transcript.

## 10. GitHub Publication and Remaining Evidence

On 18 November 2026, the developer supplied the Git terminal output confirming a successful initial push to `main`, tracking `origin/main`, at https://github.com/Skarimbilali/corporate-event-management-api. This verifies the reported local push, not public visibility or the assignment's feature-branch/merge history requirements.

The developer reported capturing Swagger UI screenshots. Submission should also include the actual complete assignment-related AI conversation history, the latest pytest result, and a genuine video recording showing the running application, PostgreSQL integration, and implemented API requests/responses. The narrated diagram-based explainer alone does not fulfill the live demonstration requirement.

## 11. Conclusion

AI assistance supported the implementation, troubleshooting, testing, and documentation of the Corporate Event Management API. The developer retained ownership of design choices and must independently verify final behavior, provide the actual AI history, and submit genuine test and demonstration evidence.

# Test execution and scope

Run from the project root:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests -v
```

The original user-supplied `pytest-results.txt` records **30 passed, 1 warning** for the original 30-test suite on Windows/Python 3.11. Additional regression tests have since been added in `test_bonus_regression.py`; run the suite again for the final total and save an updated report.

The API tests use an isolated disposable SQLite database with FastAPI TestClient and an adapter for the project's async service methods. These tests do not establish live PostgreSQL integration or the safety of simultaneous registration requests; verify those on the PostgreSQL server separately.

The application source modules and database configuration have not been changed for this documentation/testing update. JWT remains unimplemented (optional bonus).

Event deletion regression: deleting an event with registrations returns 409 without deleting data; after cancelling its registrations, deleting the event returns 204.

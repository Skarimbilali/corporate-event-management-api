"""Configure console logging for application modules only.

Existing database and Uvicorn logging settings are left untouched.
"""

import logging


def configure_logging() -> None:
    """Attach one formatter/handler to the application's logger namespace."""
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)

    if not app_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        app_logger.addHandler(handler)

    # Prevent the same message being printed twice through the root logger.
    app_logger.propagate = False

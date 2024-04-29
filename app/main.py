# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-29 18:48:17
     $Rev: 11
```
"""

# BUILTIN modules
from pathlib import Path
from dataclasses import dataclass
from contextlib import asynccontextmanager

# Third party modules
from fastapi import FastAPI
from sqlalchemy import event
from fastapi.staticfiles import StaticFiles
from sqlalchemy.dialects.sqlite.aiosqlite import AsyncAdapt_aiosqlite_connection

# Local modules
from .core.unified_logging import create_unified_logger
from .documentation import tags_metadata, description
from .sms_document.sms_document_routes import ROUTER as sms_document_router
from .sms_transfer.sms_transfer_routes import ROUTER as sms_transfer_router
from .core.database import create_async_db_tables, close_async_db, async_engine


# -----------------------------------------------------------------------------
#
@dataclass(frozen=True)
class Configuration:
    """ Configuration parameters for the FastAPI app. """
    version: str = '0.4.0'
    log_level: str = 'info'
    title: str = 'TrackingDb API'
    name: str = 'TrackingDbService'


config = Configuration()
""" A simplified config handling since this is a example that needs to be small. """


# -----------------------------------------------------------------------------
#
class Service(FastAPI):
    """
    This class adds router and image handling for the OpenAPI documentation
    as well as unified logging.

    Attributes:
        logger: logger object instance.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, *args: list, **kwargs: dict):
        """ The class constructor.

        Args:
            args: Named arguments.
            kwargs: Key-value pair arguments.
        """
        super().__init__(*args, **kwargs)

        # Needed for OpenAPI Markdown images to be displayed.
        static_path = Path(__file__).parent.parent / 'docs/images'
        self.mount("/static", StaticFiles(directory=static_path))

        # Add declared routers, note that the order visible
        # in the OpenAPI GUI is defined in the documentation
        # file (app/documentation.py).
        self.include_router(sms_document_router)
        self.include_router(sms_transfer_router)

        # Unify logging within the imported package's closure.
        self.logger = create_unified_logger(config.log_level)


# ---------------------------------------------------------
#
@asynccontextmanager
async def lifespan(_):
    """ Define startup and shutdown application logic. """
    await startup()
    yield
    await shutdown()


# ---------------------------------------------------------

app = Service(
    redoc_url=None,
    lifespan=lifespan,
    title=config.title,
    version=config.version,
    description=description,
    openapi_tags=tags_metadata,
)
""" Create the FastAPI application. """


# ---------------------------------------------------------
#
async def startup():
    """ Create asynchronous database pool and missing tables. """
    await create_async_db_tables()


# ---------------------------------------------------------
#
async def shutdown():
    """ Close asynchronous database connection pool. """
    await close_async_db()


# ---------------------------------------------------------
#
@event.listens_for(async_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection: AsyncAdapt_aiosqlite_connection, _):
    """ Enable foreign key usage on the sqlite database.

    Args:
        dbapi_connection: DB connection object.
        _: Not used (needed by signature).
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")

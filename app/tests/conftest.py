# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-30 16:38:21
     $Rev: 12
```
"""

# BUILTIN modules
import json
from pathlib import Path

# Third party modules
import pytest_asyncio
from loguru import logger
from pytest import FixtureRequest
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession

# Local modules
from ..main import app, startup
from ..core.database import async_engine
from ..sms_transfer.unit_of_work import UnitOfTransferWork
from ..sms_document.unit_of_work import UnitOfDocumentWork
from ..sms_document.sms_document_crud import SmsDocumentCrud
from ..sms_transfer.sms_transfer_crud import SmsTransferCrud

# Remove all loggers since they are not needed during testing.
logger.remove()


# ---------------------------------------------------------
#
@pytest_asyncio.fixture(scope="module")
def test_app():
    """ Starlette TestClient generator. """

    with TestClient(
            app=app,
            base_url="http://localhost/tracking"
    ) as test_client:
        yield test_client


# ---------------------------------------------------------
#
@pytest_asyncio.fixture(scope="module")
def test_data(request: FixtureRequest) -> dict:
    """ Automatically load the the unique test data file to each test module.

    Args:
        request: Contains the name of test file to load.

    Returns:
        The test data.
    """
    name = request.node.get_closest_marker("test_data").args[0]
    test_file = Path(__file__).parent / f'{name}.json'

    with open(test_file, "r") as file:
        data = json.loads(file.read())

    return data


# ---------------------------------------------------------
#
@pytest_asyncio.fixture(scope="function")
async def transfer_crud() -> SmsTransferCrud:
    """
    Create all tables if needed and return an
    active SmsTransferCrud object.

    Note that this is a DB session generator.
    """
    async with UnitOfTransferWork() as crud:
        await startup()
        yield crud


# ---------------------------------------------------------
#
@pytest_asyncio.fixture(scope="function")
async def document_crud() -> SmsDocumentCrud:
    """
    Create all tables if needed and return an
    active SmsDocumentCrud object.

    Note that this is a DB session generator.
    """
    async with UnitOfDocumentWork() as crud:
        await startup()
        yield crud

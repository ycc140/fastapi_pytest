# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-09-11 17:58:22
     $Rev: 16
```
"""

# BUILTIN modules
import json
from pathlib import Path

# Third party modules
import pytest_asyncio
from loguru import logger
from httpx import AsyncClient
from pytest import FixtureRequest

# Local modules
from ..main import app, startup
from ..core.unit_of_work import UnitOfWork
from ..sms_document.sms_document_crud import SmsDocumentCrud
from ..sms_transfer.sms_transfer_crud import SmsTransferCrud

# Remove all loggers since they are not needed during testing.
logger.remove()


# ---------------------------------------------------------
#
@pytest_asyncio.fixture(scope="function")
async def test_app():
    """ httpx AsyncClient generator. """

    async with AsyncClient(
            app=app,
            base_url="http://localhost/tracking"
    ) as client:
        yield client


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
    async with UnitOfWork(SmsTransferCrud) as crud:
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
    async with UnitOfWork(SmsDocumentCrud) as crud:
        await startup()
        yield crud

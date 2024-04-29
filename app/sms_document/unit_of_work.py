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

# Third party modules
from loguru import logger
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

# From local modules.
from ..core.database import async_engine
from .sms_document_crud import SmsDocumentCrud


# ------------------------------------------------------------------------
#
class UnitOfRepositoryWork:
    """ An async context manager class that handles SmsDocument Repository work.

    It automatically handles transaction commit when everything worked and
    rollback when an exception occurs.

    Attributes:
        session (AsyncSession): The SQLAlchemy asyncio session object.
        session_maker (sessionmaker): The SQLAlchemy ORM sessionmaker class.
    """

    # ---------------------------------------------------------
    #
    def __init__(self):
        self.session = None
        self.session_maker = sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )

    # ---------------------------------------------------------
    #
    async def __aenter__(self) -> SmsDocumentCrud:
        """ Start a DB session and return an SmsDocument repository. """
        logger.debug('Establishing SQLite session...')
        self.session = self.session_maker()
        return SmsDocumentCrud(self.session)

    # ---------------------------------------------------------
    #
    async def __aexit__(self, exc_type, exc_val, traceback):
        """ Do a commit, or rollback and end the DB session. """
        if exc_type is not None:
            logger.debug('SQLite rollback...')
            await self.session.rollback()

        else:
            logger.debug('SQLite commit...')
            await self.session.commit()

        logger.debug('Ending SQLite session...')
        await self.session.close()

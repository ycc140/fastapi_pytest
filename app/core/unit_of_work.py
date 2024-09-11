# -*- coding: utf-8 -*-
"""
```
Copyright: Ropo Capital Messaging AB

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-09-11 17:47:05
     $Rev: 15
```
"""

# BUILTIN modules
from types import TracebackType
from typing import TypeVar, Generic, Type, Optional

# Third party modules
from loguru import logger
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

# Local modules
from ..core.database import async_engine

# Typing constants
T = TypeVar("T", bound="AsyncSession")


# ------------------------------------------------------------------------
#
class UnitOfWork:
    """ An async context manager class that handles generic Repository work.

    It automatically handles transaction commit when everything worked and
    rollback when an exception occurs.

    Attributes:
        session (AsyncSession): The SQLAlchemy asyncio session object.
        crud_session_class (Any): Any CRUD class using a session object.
        async_session_maker (sessionmaker): The SQLAlchemy ORM sessionmaker class.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, crud_session_class: Generic[T]):
        """ The class constructor.

        Args:
            crud_session_class: Used CRUD session class.
        """
        self.session = None
        self.crud_session_class = crud_session_class
        self.async_session_maker = sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )

    # ---------------------------------------------------------
    #
    async def __aenter__(self) -> Generic[T]:
        """ Create an AsyncSession and return an CRUD session repository class.

        Returns:
            A CRUD model with an active DB session.
        """
        logger.debug('Establishing MySQL session...')
        self.session = self.async_session_maker()
        return self.crud_session_class(self.session)

    # ---------------------------------------------------------
    #
    async def __aexit__(
            self, exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            traceback: Optional[TracebackType]
    ):
        """ Do a commit, or rollback and end the DB session.

        Args:
            exc_type: Possible exception type.
            exc_val: Possible exception.
            traceback: Possible traceback type.
        """
        if exc_type is not None:
            logger.debug('MySQL rollback...')
            await self.session.rollback()

        else:
            logger.debug('MySQL commit...')
            await self.session.commit()

        logger.debug('Ending MySQL session...')
        await self.session.close()

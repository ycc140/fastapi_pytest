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
from uuid import UUID
from typing import List

# Third party modules
from sqlmodel import select, update, delete, func
from sqlalchemy.engine.cursor import CursorResult
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.dialects.sqlite import insert as upsert

# Local modules
from .models import (SmsTransferModel, SmsTransfer,
                     SmsTransferState, SmsTransferPayload)


# -----------------------------------------------------------------------------
#
class SmsTransferCrud:
    """ SMS Transfer CRUD operations.

    This class implements the IRepository protocol for SMS Transfer CRUD operations.

    Attributes:
        session (AsyncSession): Active SQLModel database session.
    """

    def __init__(self, session: AsyncSession):
        """ Implicit constructor.

        Args:
            session: Current DB session.
        """
        self.session = session

    # ---------------------------------------------------------
    #
    async def create(self, payload: SmsTransferPayload) -> int:
        """  Create new SMS transfer row in DB table tracking.sms_transfers.

        The UPSERT usage can come in handy when a transfer fails,
        and you have to retry sending the batch (the batch state
        and fallbackCount are reset, and the timestamp is updated).

        The DB implicitly performs the following changes during an UPSERT:
          - Sets the ``state`` value to *INIT*.
          - Sets the ``fallbackCount`` value to *0*.
          - Sets the ``when`` value to *CURRENT_TIMESTAMP*.

        Args:
            payload: SMS Transfer payload.

        Returns:
            DB upsert result.
        """
        query = (
            upsert(SmsTransferModel)
            .values(payload.model_dump())
            .on_conflict_do_update(
                index_elements=['UBID'],
                set_=dict(
                    fallbackCount=0,
                    state=SmsTransferState.INIT,
                    when=func.current_timestamp())
            )
        )
        response: CursorResult = await self.session.exec(query)
        return response.rowcount

    # ---------------------------------------------------------
    #
    async def read_all(self) -> List[SmsTransfer]:
        """ Get existing SMS transfer rows from DB table tracking.sms_transfers.

        Returns:
            List of found SMS transfer rows.
        """
        query = (
            select(SmsTransferModel)
        )
        result = await self.session.exec(query)
        return result.all()

    # ---------------------------------------------------------
    #
    async def read(self, ubid: UUID) -> SmsTransfer | None:
        """ Get specified SMS transfer row from DB table tracking.sms_transfers.

        Args:
            ubid: Batch search key.

        Returns:
            Found SMS transfer row, or None.
        """
        query = (
            select(SmsTransferModel)
            .where(SmsTransferModel.UBID == str(ubid))
        )
        result = await self.session.exec(query)
        return result.one_or_none()

    # ---------------------------------------------------------
    #
    async def update_state(self, ubid: UUID, state: SmsTransferState) -> int:
        """ Update SMS transfer row state in DB table tracking.sms_transfers.

        The DB implicitly updates the ``when`` timestamp value.

        Args:
            ubid: Batch search key.
            state: Update value.

        Returns:
            1 for successful UPDATE, 0 for failed UPDATE.
        """
        query = (
            update(SmsTransferModel)
            .where(SmsTransferModel.UBID == str(ubid))
            .values({'state': state})
        )
        response: CursorResult = await self.session.exec(query)
        return response.rowcount

    # ---------------------------------------------------------
    #
    async def delete(self, ubid: UUID) -> int:
        """ Delete specified transfer row from DB table tracking.sms_transfers.

        Args:
            ubid: Batch search key.

        Returns:
            1 for successful DELETE, 0 for failed DELETE.
        """
        query = (
            delete(SmsTransferModel)
            .where(SmsTransferModel.UBID == str(ubid))
        )
        response: CursorResult = await self.session.exec(query)
        return response.rowcount

    # ---------------------------------------------------------
    #
    async def refresh(self, model: SmsTransferModel) -> SmsTransferModel:
        """ Refresh the content of the specified DB model.

        Args:
            model: SMS Transfer DB model.

        Returns:
            DB refresh result.
        """
        return await self.session.refresh(model)

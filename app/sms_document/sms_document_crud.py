# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
   $search_date:: 2020-02-20 14:18:38
     $Rev: 15
```
"""

# BUILTIN modules
from uuid import UUID

# Third party modules
from sqlmodel import select, update, func
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.dialects.sqlite import insert as upsert

# Local modules
from ..core.database import AsyncSession
from .models import SmsDocumentModel, SmsDocumentState, SmsDocumentPayload


# -----------------------------------------------------------------------------
#
class SmsDocumentCrud:
    """ SMS Document CRUD operations.

    This class implements the IRepository protocol for SMS Document CRUD operations.

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
    async def create(self, payload: SmsDocumentPayload) -> int:
        """
        Create new SMS document row(s) in DB table
        tracking.sms_documents.

        Note that this is a BULK UPSERT operation since there
        can be thousands of documents in a batch.

        The UPSERT usage can come in handy when a transfer fails,
        and you have to retry sending the batch (the batch state
        is reset and the timestamp is updated).

        The DB implicitly performs the following changes during an UPSERT:
          - Sets the ``state`` value to *INIT*.
          - Sets the ``when`` value to *CURRENT_TIMESTAMP*.

        Args:
            payload: SMS Document payload.

        Returns:
            1 for successful Upsert, 0 for failed Upsert.
        """
        data = [
            {
                "uniqueId": doc_id,
                'data': item.smsData,
                'UBID': payload.UBID,
                "SMScount": item.SMScount,
            }
            for doc_id, item in payload.documents.items()
        ]
        query = (
            upsert(SmsDocumentModel)
            .values(data)
            .on_conflict_do_update(
                index_elements=['UBID', 'uniqueId'],
                set_=dict(
                    state=SmsDocumentState.INIT,
                    when=func.current_timestamp())
            )
        )
        response: CursorResult = await self.session.exec(query)
        await self.session.commit()
        return response.rowcount

    # ---------------------------------------------------------
    #
    async def count(self, ubid: UUID) -> int:
        """
        Return count of all SMS document(s) within a batch from DB
        table tracking.sms_documents.

        Args:
            ubid: Batch search key.

        Returns:
            Number of found SMS transfer batches.
        """
        query = (
            select(func.count(SmsDocumentModel.uniqueId))
            .where(SmsDocumentModel.UBID == str(ubid))
        )
        await self.session.exec(query)
        return await self.session.scalar(query)

    # ---------------------------------------------------------
    #
    async def update_state(self, ubid: UUID, state: SmsDocumentState) -> int:
        """
        Update state for all documents within a batch in DB table
        tracking.sms_documents.

        Args:
            ubid: Batch search key.
            state: Update value.

        Returns:
            1 for successful UPDATE, 0 for failed UPDATE.
        """
        query = (
            update(SmsDocumentModel)
            .where(SmsDocumentModel.UBID == str(ubid))
            .values({'state': state})
        )
        response: CursorResult = await self.session.exec(query)
        await self.session.commit()
        return response.rowcount

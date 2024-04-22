# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-22 16:14:44
     $Rev: 1
```
"""

# BUILTIN modules
from uuid import UUID
from typing import Protocol, List

# Local modules
from ..core.database import AsyncSession
from .models import (SmsTransferModel, SmsTransfer,
                     SmsTransferState, SmsTransferPayload)


# -----------------------------------------------------------------------------
#
class ICrudRepository(Protocol):
    """ SMS Transfer CRUD Interface class.

    Attributes:
        session (AsyncSession): Active SQLModel database session.
    """
    session: AsyncSession

    async def create(self, payload: SmsTransferPayload) -> int:
        """ Create SMS transfer row.

        If the INSERT fails due to IntegrityError do an UPDATE.

        Args:
            payload: SMS Transfer payload.

        Returns:
            1 for successful Upsert, 0 for failed Upsert.
        """

    async def read_all(self) -> List[SmsTransfer]:
        """ Get all SMS transfer rows.

        Returns:
            List of found SMS transfer rows.
        """

    async def read(self, ubid: UUID) -> SmsTransfer | None:
        """ Get specified SMS transfer row.

        Args:
            ubid: Batch search key.

        Returns:
            Found SMS transfer row, or None.
        """

    async def update_state(self, ubid: UUID, state: SmsTransferState) -> int:
        """ Update Order.

        Args:
            ubid: Batch search key.
            state: Update value.

        Returns:
            1 for successful UPDATE, 0 for failed UPDATE.
        """

    async def delete(self, ubid: UUID) -> int:
        """ Delete specified transfer row.

        Args:
            ubid: Batch search key.

        Returns:
            1 for successful DELETE, 0 for failed DELETE.
        """

    async def refresh(self, model: SmsTransferModel) -> SmsTransferModel:
        """ Refresh the content of the specified DB model.

        Args:
            model: SMS Transfer DB model.

        Returns:
            Refreshed specified DB model.
        """

# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-21 20:59:20
     $Rev: 18
```
"""

# BUILTIN modules
from uuid import UUID
from typing import Protocol

# Local modules
from ..core.database import AsyncSession
from .models import SmsDocumentState, SmsDocumentPayload


# -----------------------------------------------------------------------------
#
class ICrudRepository(Protocol):
    """ SMS Document CRUD Interface class.

    Attributes:
        session (AsyncSession): Active SQLModel database session.
    """
    session: AsyncSession

    async def create(self, payload: SmsDocumentPayload) -> int:
        """ Create new SMS document row(s).

        If the INSERT fails due to IntegrityError do an UPDATE.

        Args:
            payload: SMS Transfer payload.

        Returns:
            1 for successful Upsert, 0 for failed Upsert.
        """

    async def count(self, ubid: UUID) -> int:
        """ Return count of all SMS document(s) within a batch.

        Returns:
            Number of found SMS document(s) within a batch.
        """

    async def update_state(self, ubid: UUID, state: SmsDocumentState) -> int:
        """ Update state for all documents within a batch.

        Args:
            ubid: Batch search key.
            state: Update value.

        Returns:
            1 for successful UPDATE, 0 for failed UPDATE.
        """

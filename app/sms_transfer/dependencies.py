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

# Third party modules
from fastapi import Depends

# Local modules
from .sms_transfer_crud import SmsTransferCrud
from ..core.database import get_async_session, AsyncSession


# ---------------------------------------------------------
#
async def get_repository_crud(
        session: AsyncSession = Depends(get_async_session)) -> SmsTransferCrud:
    """ Return SMS Transfer CRUD operation instance with an active DB session.

    Args:
        session: Active SQLModel database session object.

    Returns:
        Specialized DB session for SmsTransfer CRUD operations.
    """
    return SmsTransferCrud(session=session)

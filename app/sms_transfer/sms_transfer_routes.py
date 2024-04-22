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
from typing import List

# Third party modules
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, Depends, Response, status

# Local modules
from .interface import ICrudRepository
from .dependencies import get_repository_crud
from ..core.models import UnknownError, NotFoundError
from .models import SmsTransfer, SmsTransferPayload, SmsTransferState
from ..core.documentation import ubid_documentation, state_documentation

# Constants
ROUTER = APIRouter(prefix="/tracking/sms_transfers", tags=["SMS_transfers"])
""" sms_transfers endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.post(
    "/",
    status_code=201,
    response_model=SmsTransfer,
    responses={422: {"model": UnknownError}}
)
async def create_sms_transfer_batch(
        payload: SmsTransferPayload,
        crud: ICrudRepository = Depends(get_repository_crud)
) -> SmsTransferPayload:
    """**Create new SMS transfer batch in table tracking.sms_transfers.**

    Args:
        payload: Create method payload.
        crud: DB session.

    Returns:
        DB insert result.

    Raises:
        HTTPException(422): When failed to UPSERT row in tracking.sms_transfers.
    """
    try:
        await crud.create(payload)

    except IntegrityError as why:
        errmsg = (f"Failed Upsert of UBID '{payload.UBID}' in table "
                  f"tracking.sms_transfers => {why.args[0]}")
        raise HTTPException(status_code=422, detail=errmsg)

    return payload


# ---------------------------------------------------------
#
@ROUTER.get(
    "/{ubid}/",
    response_model=List[SmsTransfer],
)
async def read_all_sms_transfer_batches(
        crud: ICrudRepository = Depends(get_repository_crud)
) -> List[SmsTransfer]:
    """
    **Return existing SMS transfer batches from table tracking.sms_transfers.**

    Args:
        crud: DB session

    Returns:
        All existing SMS transfer batches.
    """
    return await crud.read_all()


# ---------------------------------------------------------
#
@ROUTER.put(
    "/{ubid}/{state}/",
    response_model=SmsTransfer,
    responses={404: {"model": NotFoundError}}
)
async def update_sms_transfer_batch_state(
        ubid: UUID = ubid_documentation,
        state: SmsTransferState = state_documentation,
        crud: ICrudRepository = Depends(get_repository_crud)
) -> SmsTransfer:
    """**Update SMS transfer batch state in table tracking.sms_transfers.**

    Args:
        ubid: Search key.
        state: First update value.
        crud: Current DB session

    Returns:
        DB update result.

    Raises:
        HTTPException(404): When the tracking.sms_transfers row is not found.
    """
    response = await crud.read(ubid)

    if not response:
        errmsg = (f"UBID '{ubid}' is not found in "
                  f"table tracking.sms_transfers")
        raise HTTPException(status_code=404, detail=errmsg)

    await crud.update_state(ubid, state)
    await crud.refresh(response)
    return response


# ---------------------------------------------------------
#
@ROUTER.delete(
    "/{ubid}/",
    status_code=204,
    responses={404: {"model": NotFoundError}}
)
async def delete_sms_transfer_batch(
        ubid: UUID = ubid_documentation,
        crud: ICrudRepository = Depends(get_repository_crud)
):
    """**Delete SMS transfer batch in table tracking.sms_transfers.**

    Args:
        ubid: First search key.
        crud: Current DB session

    Raises:
        HTTPException(404): When the tracking.sms_transfers row is not found.
    """
    response = await crud.delete(ubid)

    if not response:
        errmsg = (f"UBID '{ubid}' is not found "
                  f"in table tracking.sms_transfers")
        raise HTTPException(status_code=404, detail=errmsg)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

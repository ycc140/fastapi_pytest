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

# BUILTIN modules
from uuid import UUID
from typing import List

# Third party modules
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, Response, status

# Local modules
from .unit_of_work import UnitOfRepositoryWork
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
async def create_sms_transfer_batch(payload: SmsTransferPayload) -> SmsTransferPayload:
    """**Create new SMS transfer batch in table tracking.sms_transfers.**

    Args:
        payload: Create method payload.

    Returns:
        DB insert result.

    Raises:
        HTTPException(422): When failed to UPSERT row in tracking.sms_transfers.
    """
    try:
        async with UnitOfRepositoryWork() as crud:
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
async def read_all_sms_transfer_batches() -> List[SmsTransfer]:
    """
    **Return existing SMS transfer batches from table tracking.sms_transfers.**

    Returns:
        All existing SMS transfer batches.
    """
    async with UnitOfRepositoryWork() as crud:
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
        state: SmsTransferState = state_documentation
) -> SmsTransfer:
    """**Update SMS transfer batch state in table tracking.sms_transfers.**

    Args:
        ubid: Search key.
        state: First update value.

    Returns:
        DB update result.

    Raises:
        HTTPException(404): When the tracking.sms_transfers row is not found.
    """
    async with UnitOfRepositoryWork() as crud:
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
async def delete_sms_transfer_batch(ubid: UUID = ubid_documentation):
    """**Delete SMS transfer batch in table tracking.sms_transfers.**

    Args:
        ubid: First search key.

    Raises:
        HTTPException(404): When the tracking.sms_transfers row is not found.
    """
    async with UnitOfRepositoryWork() as crud:
        response = await crud.delete(ubid)

    if not response:
        errmsg = (f"UBID '{ubid}' is not found "
                  f"in table tracking.sms_transfers")
        raise HTTPException(status_code=404, detail=errmsg)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

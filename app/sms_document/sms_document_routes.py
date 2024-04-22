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

# Third party modules
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, Depends

# Local modules
from .interface import ICrudRepository
from .dependencies import get_repository_crud
from ..core.models import UnknownError, NotFoundError
from .models import SmsDocumentState, SmsDocumentPayload, QueryResponse
from ..core.documentation import ubid_documentation, state_documentation

# Constants
ROUTER = APIRouter(prefix="/tracking/sms_documents", tags=["SMS_documents"])
""" sms_documents endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.post(
    "/",
    status_code=201,
    response_model=QueryResponse,
    responses={422: {"model": UnknownError}}
)
async def create_sms_transfer_batch_documents(
        payload: SmsDocumentPayload,
        crud: ICrudRepository = Depends(get_repository_crud)
) -> QueryResponse:
    """**Create SMS batch document(s) in table tracking.sms_documents.**

    Args:
      payload: Create method payload.
      crud: DB session.

    Returns:
        DB insert result.

    Raises:
        HTTPException(422): When failed to UPSERT row in tracking.sms_documents.
    """
    try:
        count = await crud.create(payload)

    except IntegrityError as why:
        errmsg = (f"Failed Upsert of UBID '{payload.UBID}' document(s) "
                  f"in table tracking.sms_documents => {why.args[0]}")
        raise HTTPException(status_code=422, detail=errmsg)

    result = (f"Inserted {count} document(s) for UBID '{payload.UBID}' "
              f"in table tracking.sms_documents")
    return QueryResponse(result=result)


# ---------------------------------------------------------
#
@ROUTER.get(
    "/{ubid}/",
    response_model=QueryResponse,
    responses={404: {"model": NotFoundError}},
)
async def count_sms_transfer_batch_documents(
        ubid: UUID = ubid_documentation,
        crud: ICrudRepository = Depends(get_repository_crud)
) -> QueryResponse:
    """
    **Return count of all SMS batch document(s) from table
    tracking.sms_documents.**

    Args:
        ubid: Batch search key.
        crud: DB session

    Returns:
        Number of found SMS transfer batch documents as statistics.

    Raises:
        HTTPException(404): When the tracking.sms_documents row is not found.
    """
    count = await crud.count(ubid)

    if not count:
        errmsg = (f"UBID '{ubid}' not found in "
                  f"table tracking.sms_documents")
        raise HTTPException(status_code=404, detail=errmsg)

    result = (f"Found {count} document(s) for UBID "
              f"'{ubid}' in table tracking.sms_documents")
    return QueryResponse(result=result)


# ---------------------------------------------------------
#
@ROUTER.put(
    "/{ubid}/{state}/",
    response_model=QueryResponse,
    responses={404: {"model": NotFoundError}}
)
async def update_sms_transfer_batch_documents_state(
        ubid: UUID = ubid_documentation,
        state: SmsDocumentState = state_documentation,
        crud: ICrudRepository = Depends(get_repository_crud)
) -> QueryResponse:
    """
    **Update state for all SMS document(s) belonging to a batch
    in table tracking.sms_documents.**

    Args:
        ubid: Batch search key.
        state: Update value.
        crud: DB session

    Returns:
        DB update statistics.

    Raises:
        HTTPException(404): When the tracking.sms_documents row is not found.
    """
    count = await crud.update_state(ubid, state)

    if not count:
        errmsg = (f"UBID '{ubid}' not found in "
                  f"table tracking.sms_documents")
        raise HTTPException(status_code=404, detail=errmsg)

    result = (f"Updated state to '{state.value}' in {count} row(s) for "
              f"UBID '{ubid}' in table tracking.sms_documents")
    return QueryResponse(result=result)

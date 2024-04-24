# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-24 21:06:12
     $Rev: 9
```
"""

# BUILTIN modules
from enum import Enum
from datetime import datetime
from typing import Optional, List

# Third party modules
from pydantic import PositiveInt, ConfigDict
from sqlalchemy.dialects.sqlite import CHAR, JSON, TIMESTAMP
from sqlmodel import SQLModel, Field, Column, ForeignKey, text

# Local modules
from ..core.models import ValidatingSQLModel
from .documentation import payload_documentation, query_response_documentation


# -----------------------------------------------------------------------------
#
class SmsDocumentState(str, Enum):
    """ SMS batch document states.

    Note that they are ordered in the correct state change order sequence.
    """
    INIT = "INIT"
    SENT = "SENT"
    DONE = "DONE"


# -----------------------------------------------------------------------------
#
class QueryResponse(SQLModel):
    """ A query response model.

    Attributes:
        result: The response from the query.
    """
    model_config = ConfigDict(json_schema_extra={"example": query_response_documentation})

    result: str = Field(max_length=170)


# -----------------------------------------------------------------------------
#
class SmsDocumentItem(SQLModel):
    """ An SMS document payload item.

    Attributes:
        data: The SMS metadata.
        SMScount: Number of 160 character block message splits.
        UBID: The SMS transfer batch ID.
        uniqueId: Unique SMS transfer ID.
    """
    data: dict
    SMScount: PositiveInt
    UBID: Optional[str] = None
    uniqueId: str = Field(max_length=10)


# -----------------------------------------------------------------------------
#
class SmsDocumentPayload(SQLModel):
    """ An SMS batch transfer Create document(s) payload model.

    Attributes:
        UBID: The SMS transfer BATCH ID.
        documents:
            A dictionary containing the SMS documents in the transfer batch.
            A limit is set to a maximum of 5000 documents.
    """
    model_config = ConfigDict(json_schema_extra={"example": payload_documentation})

    UBID: str = Field(max_length=36)
    documents: List[SmsDocumentItem] = Field(max_length=5000)


# ---------------------------------------------------------
#
class SmsDocumentModel(ValidatingSQLModel, table=True):
    """ A DB table definition for an SMS batch transfer document(s) model.

    The inheritance of the ``ValidatingSQLModel`` class activates parameter
    validation (this is not default SQLModel behaviour) when the table
    parameter is set to True.

    Note that a foreign key is defined against the SmsTransferModel
    with a cascading-delete to keep the DB integrity in good shape.

    The DB also implicitly initiates some fields when an INSERT is performed:
        - ``state`` is set to *INIT*.
        - ``when`` is set to *CURRENT_TIMESTAMP*.

    Attributes:
        UBID: The SMS transfer batch ID.
        uniqueId: Unique SMS transfer ID.
        state: SMS document state.
        SMScount: Number of 160 character block message splits.
        when: Timestamp when the document was created, or updated.
        data: The SMS metadata.
    """
    __tablename__ = "sms_documents"

    UBID: str = Field(
        sa_column=Column(
            CHAR(36), ForeignKey("sms_transfers.UBID", ondelete="CASCADE"),
            primary_key=True)
    )
    uniqueId: str = Field(max_length=10, primary_key=True)
    state: SmsDocumentState = Field(
        sa_column_kwargs={'nullable': False,
                          'server_default': SmsDocumentState.INIT}
    )
    SMScount: int = Field(nullable=False)
    when: Optional[datetime] = Field(
        default=None,
        sa_type=TIMESTAMP,
        sa_column_kwargs={'nullable': False,
                          'server_default': text("CURRENT_TIMESTAMP")}
    )
    data: dict = Field(sa_type=JSON, nullable=False)

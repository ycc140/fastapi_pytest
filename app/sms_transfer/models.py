# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-18 03:10:14
     $Rev: 8
```
"""

# BUILTIN modules
from enum import Enum
from typing import Optional
from datetime import datetime

# Third party modules
from sqlmodel import SQLModel, Field, text
from pydantic import PositiveInt, ConfigDict
from sqlalchemy.dialects.sqlite import CHAR, TIMESTAMP

# Local modules
from ..core.models import ValidatingSQLModel
from .documentation import payload_documentation, transfer_documentation


# ---------------------------------------------------------------------------
#
class SmsTransferState(str, Enum):
    """ SMS batch transfer states.

    Note that they are ordered in the correct state change order sequence.
    """

    INIT = "INIT"
    SENT = "SENT"
    DONE = "DONE"


# -----------------------------------------------------------------------------
#
class SmsTransferPayload(SQLModel):
    """ An SMS batch transfer payload model.

    Attributes:
        SMScount: Number of 160 character block message splits.
        documents: Number of SMS messages.
        UBID: The SMS transfer batch ID.
        fileName: Name of SMS transfer batch file.
        origName: Name of original file from the customer.
    """
    model_config = ConfigDict(json_schema_extra={"example": payload_documentation})

    SMScount: PositiveInt
    documents: PositiveInt
    UBID: str = Field(max_length=36)
    fileName: str = Field(max_length=55)
    origName: str = Field(max_length=50)


# -----------------------------------------------------------------------------
#
class SmsTransfer(SmsTransferPayload):
    """ An SMS batch transfer model.

    Attributes:
        when: Timestamp when the document was created, or updated.
        fallbackCount: Number of failed, or timed out messages that should be
            distributed using the fallback channel.
        state: SMS document state.
    """
    model_config = ConfigDict(json_schema_extra={"example": transfer_documentation})

    when: Optional[datetime] = None
    fallbackCount: Optional[int] = 0
    state: Optional[SmsTransferState] = SmsTransferState.INIT


# ---------------------------------------------------------
#
class SmsTransferModel(ValidatingSQLModel, table=True):
    """ A DB table definition for an SMS batch transfer model.

    The inheritance of the ``ValidatingSQLModel`` class activates parameter
    validation (this is not default SQLModel behaviour) when the table
    parameter is set to True.

    The DB also implicitly initiates some fields when an INSERT is performed:
        - ``state`` is set to *INIT*.
        - ``when`` is set to *CURRENT_TIMESTAMP*.
        - ``fallbackCount`` is set to *0*.

    Attributes:
        UBID: The SMS transfer batch ID.
        fileName: Name of SMS transfer batch file.
        origName: Name of original file from the customer.
        fallbackCount: Number of failed, or timed out messages that should be
            distributed using the fallback channel.
        when: Timestamp when the document was created, or updated.
        state: SMS document state.
        documents: Number of SMS messages.
        SMScount: Number of 160 character block message splits.
    """
    __tablename__ = "sms_transfers"

    UBID: str = Field(sa_type=CHAR(36), primary_key=True)
    fileName: str = Field(max_length=55, nullable=False)
    origName: str = Field(max_length=50, nullable=False)
    fallbackCount: int = Field(
        default=0,
        sa_column_kwargs={'nullable': False, 'server_default': text("0")}
    )
    when: Optional[datetime] = Field(
        default=None,
        sa_type=TIMESTAMP,
        sa_column_kwargs={'nullable': False,
                          'server_default': text("CURRENT_TIMESTAMP")}
    )
    state: SmsTransferState = Field(
        default=SmsTransferState.INIT,
        sa_column_kwargs={'nullable': False, 'server_default': SmsTransferState.INIT}
    )
    documents: int = Field(nullable=False)
    SMScount: int = Field(nullable=True)

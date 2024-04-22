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
from sqlmodel import SQLModel
from pydantic import ConfigDict


# -----------------------------------------------------------------------------
#
class NotFoundError(SQLModel):
    """ Defined model for the http 404 exception (Not Found).

    Attributes:
        detail: A detailed description of the error.
    """
    detail: str = "Resource not found"


# -----------------------------------------------------------------------------
#
class UnknownError(SQLModel):
    """ Defined model for the http 422 exception (Unprocessable Entity).

    Attributes:
        detail: A detailed description of the error.
    """
    detail: str = "Failed creating resource(s)"


# -----------------------------------------------------------------------------
#
class ValidatingSQLModel(SQLModel):
    """ When you inherit from this class, validation is ALWAYS performed. """
    model_config = ConfigDict(validate_assignment=True)

    def __init__(self, **kwargs):
        self.model_config['table'] = False
        super().__init__(**kwargs)
        self.model_config['table'] = True

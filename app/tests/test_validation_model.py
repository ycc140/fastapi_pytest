# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-22 06:27:39
     $Rev: 20
```
"""

# BUILTIN modules
from typing import Optional
from uuid import UUID, uuid4

# Third party modules
import pytest
from sqlmodel import Field
from pydantic import ValidationError

# Local modules
from ..core.models import ValidatingSQLModel

pytestmark = pytest.mark.test_data(__name__.rsplit('.')[-1])
""" Add the test_data fixture to all test functions in the module. """


# -----------------------------------------------------------------------------
#
class ValidationTestModel(ValidatingSQLModel, table=True):
    __tablename__ = "test"
    UBID: Optional[UUID] = Field(
        default_factory=uuid4, primary_key=True)
    uniqueId: str = Field(max_length=5, nullable=False)


# ---------------------------------------------------------
#
async def test_validation_model_ok():
    """ Test ValidatingSQLModel child with correct parameters. """

    model = ValidationTestModel(uniqueId="0001")
    assert isinstance(model, ValidatingSQLModel)


# ---------------------------------------------------------
#
async def test_validation_model_invalid(test_data: dict):
    """ Test ValidatingSQLModel child with invalid parameters.

    The following validation tests are done:
        - Test with a wrong type (int instead of str).
        - Test with a long str (exceeding size constraint).
    """

    # Test with a wrong type.
    with pytest.raises(ValidationError) as why:
        ValidationTestModel(uniqueId=1)

    assert test_data["wrong_type"] in str(why.value)

    # Test string constraint.
    with pytest.raises(ValidationError) as why:
        ValidationTestModel(uniqueId="000001")

    assert test_data["wrong_size"] in str(why.value)

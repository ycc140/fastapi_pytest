# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-30 16:38:21
     $Rev: 12
```
"""

# Third party modules
import pytest
from sqlalchemy.exc import IntegrityError

# Local modules
from ..sms_document.models import SmsDocumentPayload
from ..sms_transfer.models import SmsTransferPayload
from ..sms_document.sms_document_crud import SmsDocumentCrud
from ..sms_transfer.sms_transfer_crud import SmsTransferCrud

pytestmark = pytest.mark.test_data(__name__.rsplit('.')[-1])
""" Add the test_data fixture to all test functions in the module. """


# ---------------------------------------------------------
#
async def test_create_crud_sms_doc_batch(test_data: dict,
                                         transfer_crud: SmsTransferCrud,
                                         document_crud: SmsDocumentCrud):
    """ Test creating an SMS document batch.

    To avoid an IntegrityError, due to the foreign key constraint, we need
    to create a transfer batch first so that documents can be inserted.
    """
    payload = SmsTransferPayload(**test_data['create_transfer']['payload'])
    result = await transfer_crud.create(payload)
    assert result == test_data['create_transfer']['response']

    try:
        payload = SmsDocumentPayload(**test_data['create_document']['payload'])
        result = await document_crud.create(payload)
        assert result == test_data['create_document']['response']

    except IntegrityError:
        raise


# ---------------------------------------------------------
#
async def test_create_crud_sms_doc_fail(test_data: dict,
                                        transfer_crud: SmsTransferCrud,
                                        document_crud: SmsDocumentCrud):
    """ Test creating an SMS document batch for an unknown transfer UBID. """
    try:
        new_data = test_data.copy()
        new_data['create_document']['payload']['UBID'] = "11dfd495-dc0a-11e6-a783-00059a3c7a00"
        await test_create_crud_sms_doc_batch(new_data, transfer_crud, document_crud)

    except IntegrityError:
        assert True


# ---------------------------------------------------------
#
async def test_read_crud_sms_documents(test_data: dict,
                                       document_crud: SmsDocumentCrud):
    """ Test read all documents for specified UBID. """
    payload = test_data['count']['payload']
    result = await document_crud.count(payload)
    assert result == test_data['count']['response']


# ---------------------------------------------------------
#
async def test_read_crud_sms_unknown(test_data: dict,
                                     document_crud: SmsDocumentCrud):
    """ Test read all documents for unknown UBID. """
    payload = test_data['count_fail']['payload']
    result = await document_crud.count(payload)
    assert result == test_data['count_fail']['response']


# ---------------------------------------------------------
#
async def test_update_state_crud_sms_doc(test_data: dict,
                                         document_crud: SmsDocumentCrud):
    """ Test update state for all sms_documents. """
    payload = test_data['update_state']['payload']
    result = await document_crud.update_state(*payload)
    assert result == test_data['update_state']['response']


# ---------------------------------------------------------
#
async def test_update_state_crud_sms_fail(test_data: dict,
                                          document_crud: SmsDocumentCrud):
    """ Test creating an SMS document batch. """
    payload = test_data['update_fail']['payload']
    result = await document_crud.update_state(*payload)
    assert result == test_data['update_fail']['response']


# ---------------------------------------------------------
#
async def test_read_all_crud_sms_foreign(test_data: dict,
                                         transfer_crud: SmsTransferCrud,
                                         document_crud: SmsDocumentCrud):
    """ Test read all documents for specified UBID.

    To test the foreign key with cascading delete constraint, we need
    to delete the existing transfer batch first so that it's possible
    to verify the foreign key constraint.
    """
    ubid = test_data['create_transfer']['payload']['UBID']
    result = await transfer_crud.delete(ubid)
    assert result == test_data['create_transfer']['response']

    payload = test_data['count']['payload']
    result = await document_crud.count(payload)
    assert result == test_data['count_fail']['response']

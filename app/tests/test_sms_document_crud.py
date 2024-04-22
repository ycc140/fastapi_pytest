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

# Third party modules
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

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
                                         test_async_session: AsyncSession):
    """ Test creating an SMS document batch.

    To avoid an IntegrityError, due to the foreign key constraint, we need
    to create a transfer batch first so that documents can be inserted.
    """
    client = SmsTransferCrud(test_async_session)
    payload = SmsTransferPayload(**test_data['create_transfer']['payload'])
    result = await client.create(payload)
    assert result == test_data['create_transfer']['response']

    try:
        client = SmsDocumentCrud(test_async_session)
        payload = SmsDocumentPayload(**test_data['create_document']['payload'])
        result = await client.create(payload)
        assert result == test_data['create_document']['response']

    except IntegrityError:
        raise


# ---------------------------------------------------------
#
async def test_create_crud_sms_doc_fail(test_data: dict,
                                        test_async_session: AsyncSession):
    """ Test creating an SMS document batch for an unknown transfer UBID. """
    try:
        new_data = test_data.copy()
        new_data['create_document']['payload']['UBID'] = "11dfd495-dc0a-11e6-a783-00059a3c7a00"
        await test_create_crud_sms_doc_batch(new_data, test_async_session)

    except IntegrityError:
        assert True


# ---------------------------------------------------------
#
async def test_read_crud_sms_documents(test_data: dict,
                                       test_async_session: AsyncSession):
    """ Test read all documents for specified UBID. """
    client = SmsDocumentCrud(test_async_session)
    payload = test_data['count']['payload']

    result = await client.count(payload)
    assert result == test_data['count']['response']


# ---------------------------------------------------------
#
async def test_read_crud_sms_unknown(test_data: dict,
                                     test_async_session: AsyncSession):
    """ Test read all documents for unknown UBID. """
    client = SmsDocumentCrud(test_async_session)
    payload = test_data['count_fail']['payload']

    result = await client.count(payload)
    assert result == test_data['count_fail']['response']


# ---------------------------------------------------------
#
async def test_update_state_crud_sms_doc(test_data: dict,
                                         test_async_session: AsyncSession):
    """ Test update state for all sms_documents. """
    client = SmsDocumentCrud(test_async_session)
    payload = test_data['update_state']['payload']

    result = await client.update_state(*payload)
    assert result == test_data['update_state']['response']


# ---------------------------------------------------------
#
async def test_update_state_crud_sms_fail(test_data: dict,
                                          test_async_session: AsyncSession):
    """ Test creating an SMS document batch. """
    client = SmsDocumentCrud(test_async_session)
    payload = test_data['update_fail']['payload']

    result = await client.update_state(*payload)
    assert result == test_data['update_fail']['response']


# ---------------------------------------------------------
#
async def test_read_all_crud_sms_foreign(test_data: dict,
                                         test_async_session: AsyncSession):
    """ Test read all documents for specified UBID.

    To test the foreign key with cascading delete constraint, we need
    to delete the existing transfer batch first so that it's possible
    to verify the foreign key constraint.
    """
    client = SmsTransferCrud(test_async_session)
    ubid = test_data['create_transfer']['payload']['UBID']
    result = await client.delete(ubid)
    assert result == test_data['create_transfer']['response']

    client = SmsDocumentCrud(test_async_session)
    payload = test_data['count']['payload']

    result = await client.count(payload)
    assert result == test_data['count_fail']['response']

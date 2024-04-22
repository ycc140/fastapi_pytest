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
from sqlalchemy.ext.asyncio import AsyncSession

# Local modules
from ..sms_transfer.models import SmsTransferPayload
from ..sms_transfer.sms_transfer_crud import SmsTransferCrud

pytestmark = pytest.mark.test_data(__name__.rsplit('.')[-1])
""" Add the test_data fixture to all test functions in the module. """


# ---------------------------------------------------------
#
async def test_create_crud_sms_transfer(test_data: dict,
                                        test_async_session: AsyncSession):
    """ Test create SMS transfer data. """
    client = SmsTransferCrud(test_async_session)
    payload = SmsTransferPayload(**test_data['create_transfer']['payload'])

    result = await client.create(payload)
    assert result == test_data['create_transfer']['response']


# ---------------------------------------------------------
#
async def test_create_crud_sms_tran_fail(test_data: dict,
                                         test_async_session: AsyncSession):
    """ Test create SMS transfer data with invalid payload. """
    client = SmsTransferCrud(test_async_session)
    payload = test_data['create_fail']['payload']

    try:
        await client.create(**payload)

    except TypeError as why:
        assert why.args[0] == test_data['create_fail']['response']


# ---------------------------------------------------------
#
async def test_read_all_crud_sms_tran(test_data: dict,
                                      test_async_session: AsyncSession):
    """ Test read all SMS transfer state row(s). """
    client = SmsTransferCrud(test_async_session)

    response = await client.read_all()
    for idx, item in enumerate(response):
        want = test_data['read_all']['response'][idx]
        got = item.model_dump()

        for key, value in want.items():

            # We need to verify that we got an updated timestamp after the update.
            if key == 'when':
                assert str(got[key]) > value

            else:
                assert got[key] == value


# ---------------------------------------------------------
#
async def test_update_crud_sms_tran_state(test_data: dict,
                                          test_async_session: AsyncSession):
    """ Test update SMS transfer state row. """
    client = SmsTransferCrud(test_async_session)
    ubid = test_data['update_state']['orig']['UBID']
    state = test_data['update_state']['response']['state']

    response = await client.read(ubid)

    if response:
        await client.update_state(ubid, state)
        await client.refresh(response)

        got = response.model_dump()
        want = test_data["update_state"]["response"]

        for key, value in want.items():

            # We need to verify that we got an updated timestamp after the update.
            if key == 'when':
                assert str(got[key]) > value

            else:
                assert got[key] == value


# ---------------------------------------------------------
#
async def test_del_crud_sms_tran_batch(test_data: dict,
                                       test_async_session: AsyncSession):
    """ Test delete sms_transfer row."""
    client = SmsTransferCrud(test_async_session)

    result = await client.delete(test_data['UBID'])
    assert result == test_data['remove']


# ---------------------------------------------------------
#
async def test_del_crud_sms_tran_unknown(test_data: dict,
                                         test_async_session: AsyncSession):
    """ Test delete non-existent sms_transfer row. """
    client = SmsTransferCrud(test_async_session)
    ubid = "7ac59850-b4e8-4ab6-ad1c-5b4645ba0000"

    result = await client.delete(ubid)
    assert result == test_data['remove_not_found']

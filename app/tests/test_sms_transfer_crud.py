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

# Local modules
from ..sms_transfer.models import SmsTransferPayload
from ..sms_transfer.sms_transfer_crud import SmsTransferCrud

pytestmark = pytest.mark.test_data(__name__.rsplit('.')[-1])
""" Add the test_data fixture to all test functions in the module. """


# ---------------------------------------------------------
#
async def test_create_crud_sms_transfer(test_data: dict,
                                        transfer_crud: SmsTransferCrud):
    """ Test create SMS transfer data. """
    payload = SmsTransferPayload(**test_data['create_transfer']['payload'])
    result = await transfer_crud.create(payload)
    assert result == test_data['create_transfer']['response']


# ---------------------------------------------------------
#
async def test_create_crud_sms_tran_fail(test_data: dict,
                                         transfer_crud: SmsTransferCrud):
    """ Test create SMS transfer data with invalid payload. """
    payload = test_data['create_fail']['payload']

    try:
        await transfer_crud.create(**payload)

    except TypeError as why:
        assert why.args[0] == test_data['create_fail']['response']


# ---------------------------------------------------------
#
async def test_read_all_crud_sms_tran(test_data: dict,
                                      transfer_crud: SmsTransferCrud):
    """ Test read all the SMS transfer state row(s). """
    response = await transfer_crud.read_all()

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
                                          transfer_crud: SmsTransferCrud):
    """ Test update SMS transfer state row. """
    ubid = test_data['update_state']['orig']['UBID']
    state = test_data['update_state']['response']['state']
    response = await transfer_crud.read(ubid)

    if response:
        await transfer_crud.update_state(ubid, state)
        await transfer_crud.refresh(response)

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
                                       transfer_crud: SmsTransferCrud):
    """ Test delete sms_transfer row."""
    result = await transfer_crud.delete(test_data['UBID'])
    assert result == test_data['remove']


# ---------------------------------------------------------
#
async def test_del_crud_sms_tran_unknown(test_data: dict,
                                         transfer_crud: SmsTransferCrud):
    """ Test delete non-existent sms_transfer row. """
    ubid = "7ac59850-b4e8-4ab6-ad1c-5b4645ba0000"
    result = await transfer_crud.delete(ubid)
    assert result == test_data['remove_not_found']

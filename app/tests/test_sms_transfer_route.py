# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-05-01 17:12:04
     $Rev: 14
```
"""

# Third party modules
from httpx import AsyncClient
from pytest import mark, MonkeyPatch
from sqlalchemy.exc import IntegrityError

# Local modules
from ..sms_transfer.sms_transfer_crud import SmsTransferCrud

pytestmark = mark.test_data(__name__.rsplit('.')[-1])
""" Add the test_data fixture to all test functions in the module. """


# ---------------------------------------------------------
#
async def test_create_sms_transfer(test_data: dict,
                                   test_app: AsyncClient,
                                   monkeypatch: MonkeyPatch):
    """ Test create SMS transfer data. """

    # ---------------------------------

    async def mock_post(_, __):
        """ Monkeypatch """
        return 1

    monkeypatch.setattr(SmsTransferCrud, "create", mock_post)

    # ---------------------------------

    response = await test_app.post(
        "/sms_transfers/",
        json=test_data['create_transfer']['payload']
    )
    assert response.status_code == 201
    assert response.json() == test_data['create_transfer']['response']


# ---------------------------------------------------------
#
async def test_create_sms_tran_fail(test_app: AsyncClient):
    """ Test create SMS transfer data with invalid payload. """

    response = await test_app.post(
        "/sms_transfers/",
        json={"role": "something"}
    )
    assert response.status_code == 422


# ---------------------------------------------------------
#
async def test_create_sms_tran_exception(test_data: dict,
                                         test_app: AsyncClient,
                                         monkeypatch: MonkeyPatch):
    """ Test create SMS transfer data. """

    # ---------------------------------

    async def mock_post(_, __):
        """ Monkeypatch """
        raise IntegrityError('', orig='Something went wrong', params='')

    monkeypatch.setattr(SmsTransferCrud, "create", mock_post)

    # ---------------------------------

    response = await test_app.post(
        "/sms_transfers/",
        json=test_data['create_transfer']['payload']
    )
    assert response.status_code == 422
    assert response.json() == test_data['create_integrity_error']


# ---------------------------------------------------------
#
async def test_read_all_sms_tran(test_data: dict,
                                 test_app: AsyncClient,
                                 monkeypatch: MonkeyPatch):
    """ Test read all SMS transfer batch rows. """

    # ---------------------------------

    async def mock_get(_):
        """ Monkeypatch """
        return test_data['read_all']['response']

    monkeypatch.setattr(SmsTransferCrud, "read_all", mock_get)

    # ---------------------------------
    response = await test_app.get(
        "/sms_transfers/{UBID}/".format(**test_data)
    )
    assert response.status_code == 200
    assert response.json() == test_data['read_all']['response']


# ---------------------------------------------------------
#
async def test_update_sms_tran_state(test_data: dict,
                                     test_app: AsyncClient,
                                     monkeypatch: MonkeyPatch):
    """ Test update SMS transfer state row. """

    # ---------------------------------

    async def mock_get(_, __):
        """ Monkeypatch """
        return test_data['update_state']['orig']

    monkeypatch.setattr(SmsTransferCrud, "read", mock_get)

    # ---------------------------------

    async def mock_put(_, __, ___):
        """ Monkeypatch """
        return 0

    monkeypatch.setattr(SmsTransferCrud, "update_state", mock_put)

    # ---------------------------------

    async def mock_refresh(_, data):
        """ Monkeypatch """
        data.update(test_data['update_state']['response'])

    monkeypatch.setattr(SmsTransferCrud, "refresh", mock_refresh)

    # ---------------------------------

    url = "/sms_transfers/{UBID}/SENT/".format(**test_data)
    response = await test_app.put(url)
    assert response.status_code == 200
    assert response.json() == test_data['update_state']['response']


# ---------------------------------------------------------
#
async def test_update_sms_tran_state_error(test_data: dict,
                                           test_app: AsyncClient,
                                           monkeypatch: MonkeyPatch):
    """ Test update SMS transfer state row. """

    # ---------------------------------

    async def mock_get(_, __):
        """ Monkeypatch """
        return 0

    monkeypatch.setattr(SmsTransferCrud, "read", mock_get)

    # ---------------------------------

    url = "/sms_transfers/{UBID}/SENT/".format(**test_data)
    response = await test_app.put(url)
    assert response.status_code == 404
    assert response.json() == test_data['update_not_found']


# ---------------------------------------------------------
#
async def test_remove_sms_tran_batch(test_data: dict,
                                     test_app: AsyncClient,
                                     monkeypatch: MonkeyPatch):
    """ Test delete sms_transfer row."""

    # ---------------------------------

    async def mock_delete(_, __):
        """ Monkeypatch """
        return 1

    monkeypatch.setattr(SmsTransferCrud, "delete", mock_delete)

    # ---------------------------------

    url = "/sms_transfers/{UBID}/".format(**test_data)
    response = await test_app.delete(url)
    assert response.status_code == 204
    assert response.text == ''


# ---------------------------------------------------------
#
async def test_remove_sms_tran_unknown(test_data: dict,
                                       test_app: AsyncClient,
                                       monkeypatch: MonkeyPatch):
    """ Test delete non-existent sms_transfer row. """

    # ---------------------------------

    async def mock_delete(_, __):
        """ Monkeypatch """
        return 0

    monkeypatch.setattr(SmsTransferCrud, "delete", mock_delete)

    # ---------------------------------

    ubid = "7ac59850-b4e8-4ab6-ad1c-5b4645ba0000"
    response = await test_app.delete(f"/sms_transfers/{ubid}/")
    assert response.status_code == 404
    assert response.json() == test_data['remove_not_found']

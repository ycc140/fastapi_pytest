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
from ..sms_document.sms_document_crud import SmsDocumentCrud

pytestmark = mark.test_data(__name__.rsplit('.')[-1])
""" Add the test_data fixture to all test functions in the module. """


# ---------------------------------------------------------
#
async def test_create_sms_doc_batch(test_data: dict,
                                    test_app: AsyncClient,
                                    monkeypatch: MonkeyPatch):
    """ Test creating an SMS document batch. """

    # ---------------------------------

    async def mock_post(_, __):
        """ Monkeypatch """
        return 3

    monkeypatch.setattr(SmsDocumentCrud, "create", mock_post)

    # ---------------------------------

    response = await test_app.post(
        "/sms_documents/",
        json=test_data['create_document']['payload']
    )
    assert response.status_code == 201
    assert response.json() == test_data['create_document']['response']


# ---------------------------------------------------------
#
async def test_create_sms_doc_invalid(test_app: AsyncClient):
    """ Test create SMS documents with invalid payload. """

    response = await test_app.post(
        "/sms_documents/",
        json={"role": "something"}
    )
    assert response.status_code == 422


# ---------------------------------------------------------
#
async def test_create_sms_doc_exception(test_data: dict,
                                        test_app: AsyncClient,
                                        monkeypatch: MonkeyPatch):
    """ Test creating an SMS document batch. """

    # ---------------------------------

    async def mock_post(_, __):
        """ Monkeypatch """
        raise IntegrityError('', orig='Something went wrong', params='')

    monkeypatch.setattr(SmsDocumentCrud, "create", mock_post)

    # ---------------------------------

    response = await test_app.post(
        "/sms_documents/",
        json=test_data['create_document']['payload']
    )
    assert response.status_code == 422
    assert response.json() == test_data['create_integrity_error']


# ---------------------------------------------------------
#
async def test_read_sms_documents(test_data: dict,
                                  test_app: AsyncClient,
                                  monkeypatch: MonkeyPatch):
    """ Test read all documents for specified UBID. """

    # ---------------------------------

    async def mock_get(_, __):
        """ Monkeypatch """
        return 3

    monkeypatch.setattr(SmsDocumentCrud, "count", mock_get)

    # ---------------------------------

    url = "/sms_documents/{UBID}/".format(**test_data)
    response = await test_app.get(url)
    assert response.status_code == 200
    assert response.json() == test_data['count']


# ---------------------------------------------------------
#
async def test_read_sms_doc_exception(test_data: dict,
                                      test_app: AsyncClient,
                                      monkeypatch: MonkeyPatch):
    """ Test read all documents for specified UBID. """

    # ---------------------------------

    async def mock_get(_, __):
        """ Monkeypatch """
        return 0

    monkeypatch.setattr(SmsDocumentCrud, "count", mock_get)

    # ---------------------------------

    url = "/sms_documents/{UBID}/".format(**test_data)
    response = await test_app.get(url)
    assert response.status_code == 404
    assert response.json() == test_data['read_http_error']


# ---------------------------------------------------------
#
async def test_update_state_sms_doc(test_data: dict,
                                    test_app: AsyncClient,
                                    monkeypatch: MonkeyPatch):
    """ Test update state for all sms_documents. """

    # ---------------------------------

    async def mock_put(_, __, ___):
        """ Monkeypatch """
        return 344

    monkeypatch.setattr(SmsDocumentCrud, "update_state", mock_put)

    # ---------------------------------

    url = "/sms_documents/{UBID}/SENT/".format(**test_data)
    response = await test_app.put(url)
    assert response.status_code == 200
    assert response.json() == test_data['update_state']


# ---------------------------------------------------------
#
async def test_update_state_sms_doc_exception(test_data: dict,
                                              test_app: AsyncClient,
                                              monkeypatch: MonkeyPatch):
    """ Test update state for all sms_documents. """

    # ---------------------------------

    async def mock_put(_, __, ___):
        """ Monkeypatch """
        return 0

    monkeypatch.setattr(SmsDocumentCrud, "update_state", mock_put)

    # ---------------------------------

    url = "/sms_documents/{UBID}/SENT/".format(**test_data)
    response = await test_app.put(url)
    assert response.status_code == 404
    assert response.json() == test_data['read_http_error']

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

# BUILTIN modules
import json
import asyncio
import argparse
from uuid import uuid4

# Third party modules
from httpx import AsyncClient

# Local modules
from app.sms_transfer.models import SmsTransferPayload

# Constants
HDR_DATA = {"Content-Type": "application/json"}


# ---------------------------------------------------------
#
async def create_and_insert_batch_transfer(batch_size: int) -> str:
    """ Create and insert batch transfer.

    Args:
        batch_size: Size of the batch to create.

    Returns:
        Created batch transfer UBID.
    """
    ubid = str(uuid4())
    payload = SmsTransferPayload(UBID=ubid,
                                 SMScount=batch_size,
                                 documents=batch_size,
                                 fileName=f'{ubid}.zip',
                                 origName="20211119-01.xml")

    async with AsyncClient() as client:
        url = 'http://localhost:7000/tracking/sms_transfers/'
        response = await client.post(url=url, headers=HDR_DATA,
                                     json=payload.model_dump())

    if response.status_code != 201:
        raise RuntimeError(f"Failed to create batch transfers "
                           f"with status code {response.status_code}")

    print(f"Created batch transfers with response: "
          f"{json.dumps(response.json(), indent=4)}")
    return ubid


# ---------------------------------------------------------
#
async def create_and_insert_batch_documents(batch_size: int, ubid: str):
    """ Create and insert batch documents.

    Args:
        batch_size: Size of the batch to create.
        ubid: Unique Batch ID.
    """
    docid = 1000000001
    payload = {"UBID": ubid,
               "documents": {},
               "fileName": f'{ubid}.zip',
               "origName": "20211119-165542309564-01.xml"}

    for idx in range(batch_size):
        key = docid + idx
        payload["documents"][f'{key}'] = {
            "SMScount": 1,
            "smsData": {"refId": f"{ubid}.{key}"}}

    async with AsyncClient() as client:
        url = 'http://localhost:7000/tracking/sms_documents/'
        response = await client.post(url=url, json=payload,
                                     headers=HDR_DATA)

    if response.status_code != 201:
        raise RuntimeError(f"Failed to create batch documents "
                           f"with status code {response.status_code}")

    print(f"Created batch documents with "
          f"response: {response.json()['result']}")


# ---------------------------------------------------------
#
async def creator(args: argparse.Namespace):
    """ Create and insert a big SMS transfer batch (with documents) in the DB.

    Args:
        args: Namespace object containing command line arguments.
    """
    ubid = await create_and_insert_batch_transfer(args.batch_size)
    await create_and_insert_batch_documents(args.batch_size, ubid)


# ---------------------------------------------------------

if __name__ == "__main__":
    Form = argparse.ArgumentDefaultsHelpFormatter
    description = 'A utility script that let you create big SMS transfer batches.'
    parser = argparse.ArgumentParser(description=description, formatter_class=Form)
    parser.add_argument("batch_size", type=int, help="Specify batch size to create.")
    arguments = parser.parse_args()
    asyncio.run(creator(arguments))

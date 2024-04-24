# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-24 21:06:12
     $Rev: 9
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
API_BATCH_LIMIT = 5000
""" API request batch limit. """
HDR_DATA = {"Content-Type": "application/json"}
""" header data used for httpx requests. """


# ---------------------------------------------------------
#
async def create_and_insert_batch_transfer(batch_size: int) -> str:
    """
    Create and insert an SMS batch transfer in DB table
    tracking.sms_transfers.

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
def create_and_prepare_documents_data(batch_size: int, ubid: str) -> dict:
    """  Create and prepare SMS batch documents for DB INSERT.

    Create sub-batches that adhere to the API batch limit.

    Args:
        batch_size: Requested batch size
        ubid: Unique Batch ID.

    Returns:
        SMS documents assigned to sub-batches
        that match the API batch limit.
    """
    batch = 1
    batches = {}

    for idx in range(batch_size):
        docid = idx + 1
        key = f'{docid:010}'

        if idx > 0 and idx % API_BATCH_LIMIT == 0:
            batch += 1

        document = {
            "SMScount": 1,
            "uniqueId": key,
            "data": {
                "source": "DentalCare",
                "refId": f"{ubid}.{key}",
                "destination": f"+01708{key}",
                "userData": "Welcome to your..."}}
        batches.setdefault(batch, []).append(document)

    return batches


# ---------------------------------------------------------
#
async def send_sms_batch_documents(client: AsyncClient, batch_id: int, payload: dict):
    """
    Insert an SMS sub-batch of documents in DB table
    tracking.sms_documents.

    Args:
        client: Request response.
        batch_id: Sub-batch ID.
        payload: SMS message data.
    """
    url = 'http://localhost:7000/tracking/sms_documents/'
    response = await client.post(url=url, json=payload, headers=HDR_DATA)

    if response.status_code == 201:
        print(f"Sent sub-batch {batch_id:02} of documents "
              f"with response: {response.json()['result']}")

    else:
        print(f"ERROR: Failed to create sub-batch {batch_id:02} of "
              f"documents with status code {response.status_code} => "
              f"{response.json()['detail']}.")


# ---------------------------------------------------------
#
async def creator(args: argparse.Namespace):
    """ Create and insert a big SMS transfer batch (with documents) in the DB.

    This method can handle any specified batch size since it will
    create sub-batches to adhere to the API batch limit.

    Args:
        args: Namespace object containing command line arguments.
    """
    ubid = await create_and_insert_batch_transfer(args.batch_size)
    sub_batches = create_and_prepare_documents_data(args.batch_size, ubid)

    async with AsyncClient() as client:
        for batch_id, documents in sub_batches.items():
            payload = {"UBID": ubid, "documents": documents}
            await asyncio.create_task(
                send_sms_batch_documents(client, batch_id, payload)
            )


# ---------------------------------------------------------

if __name__ == "__main__":
    Form = argparse.ArgumentDefaultsHelpFormatter
    description = 'A utility script that let you create bigger SMS transfer batches.'
    parser = argparse.ArgumentParser(description=description, formatter_class=Form)
    parser.add_argument("batch_size", type=int, help="Specify batch size to create.")
    arguments = parser.parse_args()
    asyncio.run(creator(arguments))

# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-23 11:38:26
     $Rev: 4
```
"""

# BUILTIN modules
import json
import asyncio
import argparse
from uuid import uuid4
from collections import ChainMap

# Third party modules
from httpx import AsyncClient

# Local modules
from app.sms_transfer.models import SmsTransferPayload

# Constants
API_BATCH_LIMIT = 5000
""" Request batch limit used with httpx requests. """
HDR_DATA = {"Content-Type": "application/json"}
""" header data used for httpx requests. """


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

    This method can handle any specified batch size since it will
    create sub-batches to adhere to the API batch limit.

    Args:
        batch_size: Size of the batch to create.
        ubid: Unique Batch ID.
    """
    documents = []
    docid = 1000000001
    stop = API_BATCH_LIMIT
    payload = {"UBID": ubid,
               "documents": {},
               "fileName": f'{ubid}.zip',
               "origName": "20211119-165542309-01.xml"}
    url = 'http://localhost:7000/tracking/sms_documents/'

    # Create a list that holds all requested documents in the batch.
    for idx in range(batch_size):
        key = docid + idx
        documents.append({f'{key}': {
            "SMScount": 1,
            "smsData": {"refId": f"{ubid}.{key}"}}})

    async with AsyncClient() as client:

        # Create sub-batches that adhere to the API documents batch limit.
        for start in range(0, batch_size, API_BATCH_LIMIT):

            # Create a documents dict with the correct batch limit.
            payload["documents"] = dict(ChainMap(*documents[start:stop]))

            # Insert the data in the database.
            response = await client.post(url=url, json=payload, headers=HDR_DATA)

            if response.status_code == 201:
                print(f"Sent batch documents with "
                      f"response: {response.json()['result']}")

            else:
                print(f"ERROR: Failed to create batch documents with status "
                      f"code {response.status_code} => {response.json()['detail']}.")

            # update stop index for next iteration
            stop += API_BATCH_LIMIT


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
    description = 'A utility script that let you create bigger SMS transfer batches.'
    parser = argparse.ArgumentParser(description=description, formatter_class=Form)
    parser.add_argument("batch_size", type=int, help="Specify batch size to create.")
    arguments = parser.parse_args()
    asyncio.run(creator(arguments))

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

payload_documentation = {
    "UBID": "2a168739-b204-4abf-aec1-a88069e3cd08",
    "documents": [
        {
            "SMScount": 1,
            "uniqueId": "1000019152",
            "data": {
                "source": "DentalCare",
                "destination": "+01708804622",
                "userData": "Welcome to your...",
                "refId": "2a168739-b204-4abf-aec1-a88069e3cd08.0000019152"
            },
        },
        {
            "SMScount": 1,
            "uniqueId": "1000019153",
            "data": {
                "source": "DentalCare",
                "destination": "+01708804623",
                "userData": "Welcome to your...",
                "refId": "2a168739-b204-4abf-aec1-a88069e3cd08.0000019153"
            },
        },
        {
            "SMScount": 1,
            "uniqueId": "1000019154",
            "data": {
                "source": "DentalCare",
                "destination": "+01708804624",
                "userData": "Welcome to your...",
                "refId": "2a168739-b204-4abf-aec1-a88069e3cd08.0000019154"
            },
        }
    ]
}
""" OpenAPI SmsDocumentPayload example documentation. """

query_response_documentation = {
    "result": "Inserted/Found/Updated 3 document(s) for UBID "
              "'2a168739-b204-4abf-aec1-a88069e3cd08' in table tracking.sms_documents"
}
""" OpenAPI Query response example documentation. """

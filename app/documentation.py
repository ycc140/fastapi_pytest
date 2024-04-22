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

tags_metadata = [
    {
        "name": "SMS_transfers",
        "description": "These endpoints handles SMS transfer batches.",
    },
    {
        "name": "SMS_documents",
        "description": "These endpoints handles SMS transfer batch documents.",
    },
]
""" OpenAPI UBID endpoint tags documentation. """

description = """
**This is a RESTful API portal with 7 URL endpoints distributed over 2 groups that interfaces 2 SQLite
tables in the ``tracking`` database.**
<br><br>
![image](/static/overview.png)
<br><br>
---
"""
""" OpenAPI master documentation. """

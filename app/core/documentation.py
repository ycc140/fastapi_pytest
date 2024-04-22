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

# Third party modules
from fastapi import Path

ubid_documentation = Path(
    ...,
    description='Specify a **U**nique **B**atch **ID** to search for.<br>'
                '*Example: `2a168739-b204-4abf-aec1-a88069e3cd08`*'
)
""" OpenAPI UBID Path documentation. """

state_documentation = Path(
    ...,
    description='Specify the desired state to use'
)
""" OpenAPI state Path documentation. """

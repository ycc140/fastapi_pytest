# -*- coding: utf-8 -*-
"""
```
License: Apache 2.0

VERSION INFO:
    $Repo: fastapi_pytest
  $Author: Anders Wiklund
    $Date: 2024-04-18 03:10:14
     $Rev: 8
```
"""

# Third party modules
import uvicorn

# Local modules
from app.main import app, config


# ---------------------------------------------------------
#
def main():
    """ Start uvicorn program. """
    uv_config = {'log_level': config.log_level,
                 'app': 'app.main:app', 'port': 7000, 'reload': False,
                 'log_config': {"disable_existing_loggers": False, "version": 1}}
    app.logger.info(f'{config.name} v{config.version} is initializing...')
    uvicorn.run(**uv_config)


if __name__ == "__main__":
    main()

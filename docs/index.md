# Welcome to the TrackingDb API example

This is a python FastAPI API example that provides a database abstraction
layer for its users.

Used base components are:

  * FastAPI
  * SQLModel
  * aiosqlite
  * Loguru
  * uvicorn.
  * pytest

Although the Database used in the example is SQLite (to make it easier for you), the
call chain is still fully asynchronous, and it's using DB transaction sessions
for each API call from a connection pool.

Replacing it with the relational database of your choice will be fairly
easy due to the used Repository design pattern implementation.

The following techniques are incorporated and explained in the example:

  * Using the Repository and the Dependency Injection design patterns.
  * Using DB foreign key table linking with a cascading delete constraint.
  * Using bulk `Upsert` techniques with SQLModel and alchemy ORM handling.
  * Using colorized and unified logs with the same formatting for all components.
  * Explains how and where to add OpenAPI documentation to enrich the user experience.
  * How to get SQLModel to do validation even when the `table=True` flag is set.
  * How to perform testing of the API without using the database.
  * How to use test data for each test module from its own test data file.

## Example overview

The following picture shows the logical structure of the example:

![image](images/overview.png)

## Directory structure
This is the directory structure of the example. The docs directory structure has been omitted for clarity reasons.

    📂 fastapi_pytest
    ├──📃 insert_big_batch.py
    ├──📃 mkdocs.yml
    ├──📃 requirements.txt
    ├──📃 requirements_mkdocs.txt
    ├──📃 run.py
    ├──📃 __init__.py
    └──📂 app
       ├──📃 documentation.py
       ├──📃 main.py
       ├──📃 pytest.ini
       ├──📃 __init__.py
       ├──📂 core
       │  ├──📃 database.py
       │  ├──📃 documentation.py
       │  ├──📃 models.py
       │  ├──📃 unified_logging.py
       │  └──📃 __init__.py
       ├──📂 sms_document
       │  ├──📃 dependencies.py
       │  ├──📃 documentation.py
       │  ├──📃 interface.py
       │  ├──📃 models.py
       │  ├──📃 sms_document_crud.py
       │  ├──📃 sms_document_routes.py
       │  └──📃 __init__.py
       ├──📂 sms_transfer
       │  ├──📃 dependencies.py
       │  ├──📃 documentation.py
       │  ├──📃 interface.py
       │  ├──📃 models.py
       │  ├──📃 sms_transfer_crud.py
       │  ├──📃 sms_transfer_routes.py
       │  └──📃 __init__.py
       └──📂 tests
          ├──📃 conftest.py
          ├──📃 test_sms_document_crud.json
          ├──📃 test_sms_document_crud.py
          ├──📃 test_sms_document_route.json
          ├──📃 test_sms_document_route.py
          ├──📃 test_sms_transfer_crud.json
          ├──📃 test_sms_transfer_crud.py
          ├──📃 test_sms_transfer_route.json
          ├──📃 test_sms_transfer_route.py
          ├──📃 test_validation_model.json
          ├──📃 test_validation_model.py
          └──📃 __init__.py

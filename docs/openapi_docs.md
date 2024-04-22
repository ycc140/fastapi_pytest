FastAPI automatically creates the OpenAPI (previously named swagger) documentation
that you can interact with when you start your app with `uvicorn`. This is a bare-bone
version that can be enriched in many ways to make it easier for the user of the API.

I have added some enrichments to make the testing a lot easier when it comes to
input data, or understanding what to input, as well as example responses to the
different API calls.

I have added graphics and endpoint descriptions to the starting page by adding it
to the instantiation of the FastAPI app like this:

### central enrichments

``` py linenums="1" hl_lines="3-6 15-16" title="app/main.py"
@dataclass(frozen=True)
class Configuration:
    version: str = '0.3.0'
    log_level: str = 'info'
    title: str = 'TrackingDb API'
    name: str = 'TrackingDbService'

config = Configuration()

app = Service(
    redoc_url=None,
    lifespan=lifespan,
    title=config.title,
    version=config.version,
    description=description,
    openapi_tags=tags_metadata,
)
```

Configuration parameters, shown in the first highlight, are inserted in lines 13–14.
The other highlight on line 15–16 is imported and inserted from the following file:

``` py linenums="1" hl_lines="1 12" title="app/documentation.py"
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

description = """
**This is a RESTful API portal with 7 URL endpoints distributed over 2 groups that interfaces 2 SQLite
tables in the ``tracking`` database.**
<br><br>
![image](/static/overview.png)
<br><br>
---
"""
```

### model enrichments

This is an example of adding the enrichment to an SQLModel. Doing it this way,
you'll get the correct payload parameters that you can use when you want to
insert a row in the DB.

The highlighted line below shows how to add the enrichment.

``` py linenums="1" hl_lines="2" title="app/sms_transfer/models.py"
class SmsTransferPayload(SQLModel):
    model_config = ConfigDict(json_schema_extra={"example": payload_documentation})

    SMScount: PositiveInt
    documents: PositiveInt
    UBID: str = Field(max_length=36)
    fileName: str = Field(max_length=55)
    origName: str = Field(max_length=50)
```

The enrichment itself looks like this:

``` py linenums="1" hl_lines="1" title="app/sms_transfer/documentation.py"
payload_documentation = {
    "SMScount": 4,
    "documents": 2,
    "origName": "20211119-165542309564-01.xml",
    "UBID": "2a168739-b204-4abf-aec1-a88069e3cd08",
    "fileName": "2a168739-b204-4abf-aec1-a88069e3cd08.zip"
}
```

### input Path parameter enrichments

The first highlight below on line four adds the error declaration to the response block
of the OpenAPI documentation.

The second highlight on line seven is an example of enriching an input `Path` parameter.
It explains what it is and what an example of it looks like.

``` py linenums="1" hl_lines="4 7" title="app/sms_transfer/sms_transfer_routes.py"
@ROUTER.delete(
    "/{ubid}/",
    status_code=204,
    responses={404: {"model": NotFoundError}}
)
async def delete_sms_transfer_batch(
        ubid: UUID = ubid_documentation,
        crud: ICrudRepository = Depends(get_repository_crud)
):
    response = await crud.delete(ubid)

    if not response:
        errmsg = (f"UBID '{ubid}' is not found "
                  f"in table tracking.sms_transfers")
        raise HTTPException(status_code=404, detail=errmsg)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

The `Path` enrichment looks like this:

``` py linenums="1" hl_lines="1" title="app/core/documentation.py"
ubid_documentation = Path(
    ...,
    description='Specify a **U**nique **B**atch **ID** to search for.<br>'
                '*Example: `2a168739-b204-4abf-aec1-a88069e3cd08`*'
)
```

Have these enrichments in mind when you run the example, and you will see the
benefits they bring. Then it's totally up to you if this is something that will
benefit your own APIs or not.

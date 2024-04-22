The tests are basically grouped into two parts.
One focuses on the API endpoints, the other on the CRUD part.

The CRUD part tests the DB handling without using the API endpoints, and it's using a
separate database for this.
The API endpoint part uses monkey-patching to isolate itself from the database functionality.

## pytest MonkeyPatch

I use monkey patching to simulate calls to the CRUD operations. A test case can look like this:

``` py linenums="1" hl_lines="7-10" title="app/tests/test_sms_documents.py"
async def test_create_sms_transfer(test_data: dict,
                                   test_app: TestClient,
                                   monkeypatch: pytest.MonkeyPatch):

    # ---------------------------------

    async def mock_post(_, __):
        return 1

    monkeypatch.setattr(SmsTransferCrud, "create", mock_post)

    # ---------------------------------

    response = test_app.post("/tracking/sms_transfers/",
                             json=test_data['create_transfer']['payload'])

    assert response.status_code == 201
    assert response.json() == test_data['create_transfer']['response']
```

The highlighted part is where the patching occurs. The `create` method of the
`SmsTransferCrud` class is monkey-patched into using the  `mock_post ` function
instead. So, when the endpoint code calls the `create` method, the call will be
rerouted to this function. For this to work, it needs to look and respond like
the real method does (if it walks like a duck and talks like a duck, it's a...).

As a side note, the mock_post input parameters might look a little bit weird
(underscores), but it's a python coding convention for when the input values are not used.

For you to get a feel for this, this is what it looks like in the endpoint code:

``` py linenums="1" hl_lines="11" title="app/sms_document/sms_transfer_routes.py"
@ROUTER.post(
    "/",
    status_code=201,
    response_model=SmsTransfer,
    responses={422: {"model": UnknownError}}
)
async def create_sms_transfer_batch(
        payload: SmsTransferPayload,
        crud: ICrudRepository = Depends(get_repository_crud)
) -> SmsTransferPayload:
    try:
        await crud.create(payload)

    except IntegrityError as why:
        errmsg = (f"Failed Upsert of UBID '{payload.UBID}' in table "
                  f"tracking.sms_transfers => {why.args[0]}")
        raise HTTPException(status_code=422, detail=errmsg)

    return payload
```

The confusion that might occur in your mind when you notice that the highlighted `create` method
only has one input parameter but `mock_post` has two; just dissipates when you realize that the
first implicit parameter in a call to a class method always is the `self` parameter.

This is the monkey-patching technique used in the testing. When you combine this technique with
the separate test data files described in the next section, testing is a lot cleaner and easier.

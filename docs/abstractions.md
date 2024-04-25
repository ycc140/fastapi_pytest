There are many good design patterns that will make your code better, more maintainable
and stable from future requirement changes.

For example, you have the [SOLID](https://en.wikipedia.org/wiki/SOLID) design principles
and [GRASP](https://en.wikipedia.org/wiki/GRASP_(object-oriented_design)). Both contain
a number of usable design patters to use.

I have chosen to highlight two of the design patterns that I have used in this example.

### Repository design pattern

??? note "A Repository design pattern definition"

    The Repository Pattern is a fundamental design pattern in software development
    that provides an abstraction layer between the application’s data access logic
    and the underlying data source. It promotes separation of concerns and enhances
    code maintainability, testability, and scalability.

In this example, I have separated the CRUD database operations from the API endpoints.
Besides making the code more maintainable and easier to read, due to the abstraction,
it also simplifies the testing.

The separation is created by defining an interface for the CRUD operations that the endpoints
can reference.
This interface is implemented using the python
[Protocol](https://typing.readthedocs.io/en/latest/spec/protocol.html#protocols) class.
The CRUD class implements the methods defined in the interface.

The API endpoint expects the CRUD class to look and behave as specified in the interface,
and the CRUD code has to adhere to the interface definitions for it to work.
One of the advantages of using this pattern is that, if two developers are working on this together.
The API endpoint guy can develop a quick, in memory implementation of the interface using
a dict to handle the data while the other guy is developing the final CRUD version that
contains ORM code accessing a database.
The endpoint guy doesn't have to wait for the
final CRUD code to be available to start developing his part of the assignment.

For the following code snippets, the inline documentation is removed to keep the size down.

#### interface

The `sms_transfer` interface class looks like this:

``` py linenums="1" title="snippet from app/sms_transfer/interface.py"
class ICrudRepository(Protocol):
    session: AsyncSession

    async def create(self, payload: SmsTransferPayload) -> int:

    async def read_all(self) -> List[SmsTransfer]:

    async def read(self, ubid: UUID) -> SmsTransfer | None:

    async def update_state(self, ubid: UUID, state: SmsTransferState) -> int:

    async def delete(self, ubid: UUID) -> int:

    async def refresh(self, model: SmsTransferModel) -> SmsTransferModel:
```

#### CRUD implementation of the interface

The CRUD `create` method that's called looks like this:

``` py linenums="1" title="snippet from app/sms_transfer/sms_transfer_crud.py"
async def create(self, payload: SmsTransferPayload) -> int:
    query = (
        upsert(SmsTransferModel)
        .values(payload.model_dump())
        .on_conflict_do_update(
            index_elements=['UBID'],
            set_=dict(
                fallbackCount=0,
                state=SmsTransferState.INIT,
                when=func.current_timestamp())
        )
    )
    response: CursorResult = await self.session.exec(query)
    await self.session.commit()
    return response.rowcount
```

There's a lot of ORM stuff going on in there, that can be ignored for now.
We are going to talk about this in more detail later on.

#### Creating CRUD access for the endpoint route

This shows how the DB session connects to the specific CRUD implementation:

``` py linenums="1" title="snippet from app/sms_transfer/dependencies.py"
async def get_repository_crud(
        session: AsyncSession = Depends(get_async_session)) -> SmsTransferCrud:
    return SmsTransferCrud(session=session)
```

It's placed in a separate file, instead of having it in the CRUD or route file,
to reduce dependencies and keep the code loosely coupled.

#### Endpoint route

This is what it looks like in the code for a API endpoint:

``` py linenums="1" hl_lines="9" title="snippet from app/sms_transfer/sms_transfer_routes.py"
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

All the CRUD details for this POST endpoint are *hidden* behind the highlighted line 9.
Notice that it's the interface class that the type hint is pointing to, not the actual
CRUD implementation.

### Dependency Injection design pattern

??? note "A Dependency Injection design pattern definition"

    In software engineering, dependency injection is a design pattern in which
    an object or function receives other objects or functions that it depends
    on. A form of inversion of control, dependency injection aims to separate
    the concerns of constructing objects and using them, leading to loosely coupled programs.

This pattern is implemented in FastAPI by the [Depends](https://fastapi.tiangolo.com/tutorial/dependencies)
function, and I'm using it to insert DB sessions into the CRUD classes to keep the code loosely-coupled.

This is a three-layer coding technique that starts in the database module like this:

``` py linenums="1" title="snippet from app/core/database.py"
async def get_async_session() -> AsyncSession:
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
```

This function is what's called a python generator (what is a generator? it's explained
[here](https://wiki.python.org/moin/Generators)).

This shows how the `get_async_session` function connects to the specific CRUD implementation:

``` py linenums="1" title="snippet from app/sms_transfer/dependencies.py"
async def get_repository_crud(
        session: AsyncSession = Depends(get_async_session)) -> SmsTransferCrud:
    return SmsTransferCrud(session=session)
```

This function is then used in the endpoint like this:

``` py linenums="1" hl_lines="6" title="snippet from app/sms_transfer/sms_transfer_routes.py"
@ROUTER.get(
    "/{ubid}/",
    response_model=List[SmsTransfer],
)
async def read_all_sms_transfer_batches(
        crud: ICrudRepository = Depends(get_repository_crud)
) -> List[SmsTransfer]:
    return await crud.read_all()
```

The highlighted line 6 shows how the endpoint gets access to the CRUD code
that's already injected with an active DB session.

This makes it a good design with loosely coupled code in my eyes. This might not
be the way that everybody prefers to code their APIs, and that is fine. To each their own.

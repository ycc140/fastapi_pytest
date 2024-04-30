There are many good design patterns that will make your code better, more maintainable
and stable from future requirement changes.

For example, you have the [SOLID](https://en.wikipedia.org/wiki/SOLID) design principles
and [GRASP](https://en.wikipedia.org/wiki/GRASP_(object-oriented_design)). Both contain
a number of usable design patters to use.

I have chosen to highlight three of the design patterns that I have used in this example.

### Repository design pattern

??? note "A Repository design pattern definition"

    The Repository Pattern is a fundamental design pattern in software development
    that provides an abstraction layer between the application’s data access logic
    and the underlying data source. It promotes separation of concerns and enhances
    code maintainability, testability, and scalability.

In this example, I have separated the CRUD database operations from the API endpoints.
Besides making the code more maintainable and easier to read, due to the abstraction,
it also simplifies the testing.

### Unit-of-Work design pattern

??? note "A Unit of Work design pattern definition"

    A unit of work is a behavioral pattern in software development. Martin Fowler
    has defined it as everything one does during a business transaction which can
    affect the database. When the unit of work is finished, it will provide
    everything that needs to be done to change the database as a result of the work.

I have implemented this pattern as a context manager.
It's used for creating database sessions and automatically performing the Commit
and Rollback when required.

### Dependency Injection design pattern

??? note "A Dependency Injection design pattern definition"

    In software engineering, dependency injection is a design pattern in which
    an object or function receives other objects or functions that it depends
    on. A form of inversion of control, dependency injection aims to separate
    the concerns of constructing objects and using them, leading to loosely coupled programs.

This pattern is used for inserting the database session into the CRUD classes to
keep the code loosely coupled.

### Code snippets to show how the patterns are implemented and used

For the following code snippets, the inline documentation is removed to keep the size down.

#### CRUD implementation

A CRUD `create` method that's called looks like this:

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
    return response.rowcount
```

There's a lot of ORM stuff going on in there, that can be ignored for now.
We are going to talk about this in more detail later on.

#### Creating CRUD access for the endpoint route

The highlighted lines below show how the context manager creates a DB session,
connects it to the specific CRUD implementation and return the CRUD instance.
The `__aexit__` method shows handles the automatic `rollback`, or `commit`
commands as well as closing the active session:

``` py linenums="1" hl_lines="11-12" title="app/sms_transfer/unit_of_work.py"
class UnitOfTransferWork:

    def __init__(self):
        self.session = None
        self.session_maker = sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )

    async def __aenter__(self) -> SmsTransferCrud:
        logger.debug('Establishing SQLite session...')
        self.session = self.session_maker()
        return SmsTransferCrud(self.session)

    async def __aexit__(self, exc_type, exc_val, traceback):
        if exc_type is not None:
            logger.debug('SQLite rollback...')
            await self.session.rollback()

        else:
            logger.debug('SQLite commit...')
            await self.session.commit()

        logger.debug('Ending SQLite session...')
        await self.session.close()
```

#### Endpoint route

This is what it looks like in the code for an API endpoint:

``` py linenums="1" hl_lines="9-10" title="snippet from app/sms_transfer/sms_transfer_routes.py"
@ROUTER.post(
    "/",
    status_code=201,
    response_model=SmsTransfer,
    responses={422: {"model": UnknownError}}
)
async def create_sms_transfer_batch(payload: SmsTransferPayload) -> SmsTransferPayload:
    try:
        async with UnitOfTransferWork() as crud:
            await crud.create(payload)

    except IntegrityError as why:
        errmsg = (f"Failed Upsert of UBID '{payload.UBID}' in table "
                  f"tracking.sms_transfers => {why.args[0]}")
        raise HTTPException(status_code=422, detail=errmsg)

    return payload
```

All the CRUD details for this POST endpoint are *hidden* behind the highlighted lines.

This makes it a good design with loosely coupled code in my eyes. This might not
be the way that everybody prefers to code their APIs, and that is fine. To each their own.

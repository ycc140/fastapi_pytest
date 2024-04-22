There are som interesting parts of the `SmsDocumentModel` that I want to point out.

``` py linenums="1" hl_lines="6 12 19" title="app/sms_document/models.py"
class SmsDocumentModel(ValidatingSQLModel, table=True):
    __tablename__ = "sms_documents"

    UBID: str = Field(
        sa_column=Column(
            CHAR(36), ForeignKey("sms_transfers.UBID", ondelete="CASCADE"),
            primary_key=True)
    )
    uniqueId: str = Field(max_length=10, primary_key=True)
    state: SmsDocumentState = Field(
        sa_column_kwargs={'nullable': False,
                          'server_default': SmsDocumentState.INIT}
    )
    SMScount: int = Field(nullable=False)
    when: Optional[datetime] = Field(
        default=None,
        sa_type=TIMESTAMP,
        sa_column_kwargs={'nullable': False,
                          'server_default': text("CURRENT_TIMESTAMP")}
    )
    data: dict = Field(sa_type=JSON, nullable=False)
```

### Foreign key constraint

The highlighted line 6 defines a foreign key with a cascading delete
constraint. This means that the two tables are linked via their UBID columns in
a parent-child relationship, with the code shown above becoming the child.

This means that:

  * You can't insert any documents in the `sms_documents` table if a row in the
    `sms_transfers` table with the same UBID doesn't exist.
  * When you delete a row in the `sms_transfers` table, all rows in the
    `sms_documents` table with the same UBID will also be deleted.

This is excellent when it comes to database integrity, making sure no orphans will
exist in the `sms_documents` table.

Using foreign key functionality in relational databases, like MySQL/MariaDb or
PostgreSQL isn't a problem, but for SQLite there is an issue that needs to be handled.
Foreign key functionality is not activated by default. It has to be activated every
time you open the database if you want to use it.

By using the tools available to us, this can easily be handled in a good way, as the
following snippet shows.

``` py linenums="1" title="app/main.py"
@event.listens_for(async_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection: AsyncAdapt_aiosqlite_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
```

### Defining default DB table parameter values

The last two highlights in the previous models file show how to define default
values that the DB table will use when a row is inserted and these parameters
are not supplied.

The last highlight, on row 19 in the previous models file is special in that it's
a dynamic value, it inserts the current timestamp for the missing parameter when
the table row is created.

### Bypassing SQLModel non-validation of parameters when table=True

There's a known problem with this, or maybe not a problem but more of a design
decision made by the developer. Regardless of the reason, I have made a validation
class to inherit from that re-activates the validation. For me, it doesn't cause any
DB type conversion problems, so it feels good to have activated validation for all my
SQLModel objects.

Line 1 in the previous models file shows the inheritance from the
`ValidatingSQLModel` class, that's all that is needed to activate the validation.

This is a snippet of a test file to verify that the validation works:

``` py title="app/tests/test_validation_model.py"
class ValidationTestModel(ValidatingSQLModel, table=True):
    __tablename__ = "test"
    UBID: Optional[UUID] = Field(
        default_factory=uuid4, primary_key=True)
    uniqueId: str = Field(max_length=5, nullable=False)


async def test_validation_model_ok():
    model = ValidationTestModel(uniqueId="0001")
    assert isinstance(model, ValidatingSQLModel)


async def test_validation_model_invalid(test_data: dict):

    # Test with a wrong type.
    with pytest.raises(ValidationError) as why:
        ValidationTestModel(uniqueId=1)

    assert test_data["wrong_type"] in str(why.value)

    # Test string constraint.
    with pytest.raises(ValidationError) as why:
        ValidationTestModel(uniqueId="000001")

    assert test_data["wrong_size"] in str(why.value)
```

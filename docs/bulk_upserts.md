When you want to insert a lot of database rows at the same time, it's not efficient
to do an INSERT for every row, instead you use a bulk insert technique with one
INSERT for all the rows (or you batch them if there is a lot of rows to insert).

Another problem with inserts is that sometimes when you try to insert a row, you get
an error, saying that the row already exists. This happens when you are using primary
keys to make sure that every row in your table is unique (another technique for maintaining
a good database integrity).

When that happens, your code that made the database call has to decide how to handle that.
Usually what happens is that you try to UPDATE some columns in the existing DB row instead,
like updating the state, or the timestamp.

Instead of having to do two calls to the database, you can make what's known as an *Upsert* call,
which is a combination of INSERT and UPDATE in one call.

There are slight changes in how to write the code depending on which relational database you are using.
More details on how to implement this for the dialect of your preferred database that you are using can
be found in the sqlalchemy documentation. For example, on how to do an upsert in
[MySQL/MariaDB](https://docs.sqlalchemy.org/en/20/dialects/mysql.html#mysql-insert-on-duplicate-key-update),
or [PostgreSQL](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#insert-on-conflict-upsert).

### bulk upserts

``` py linenums="1" hl_lines="2-10 14-19" title="app/sms_document/sms_document_crud.py"
async def create(self, payload: SmsDocumentPayload) -> int:
    data = [
        {
            "uniqueId": doc_id,
            'data': item.smsData,
            'UBID': payload.UBID,
            "SMScount": item.SMScount,
        }
        for doc_id, item in payload.documents.items()
    ]
    query = (
        upsert(SmsDocumentModel)
        .values(data)
        .on_conflict_do_update(
            index_elements=['UBID', 'uniqueId'],
            set_=dict(
                state=SmsDocumentState.INIT,
                when=func.current_timestamp())
        )
    )
    response: CursorResult = await self.session.exec(query)
    await self.session.commit()
    return response.rowcount
```

The first highlight shows how to create a list of the documents that you want to
use for the bulk INSERT, or possibly UPDATE.
The created list is added to the query on line 13.

The second highlight shows `conflict_db_update`. That is what kicks in when there's
a primary key conflict. In my case the `state` is reset and the` when` timestamp is updated.

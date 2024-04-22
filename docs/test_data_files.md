## A good technique when using test files

I recently discovered that it's possible to use a two-way communication technique
with the pytest fixtures. Some might call me a late bloomer (oh, we have known about
that for years), but still, this little gem intrigued me a lot. It comes in quite
handy when you want each test module to use its own file with test data.

The content of the tests directory looks like this:

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

In the test configuration file, the following fixture is what does the bulk of the work:

``` py linenums="1" hl_lines="1 3" title="app/tests/conftest.py"
@pytest.fixture(scope="module")
def test_data(request: FixtureRequest) -> dict:
    name = request.node.get_closest_marker("test_data").args[0]
    test_file = Path(__file__).parent / f'{name}.json'

    with open(test_file, "r") as file:
        data = json.loads(file.read())

    return data
```

The first highlight on line one defines the scope as module; this means that the fixture
is called once for every test file (instead of for every test case within the file).

The second highlight on line three is what extracts the filename that the test
modul requested.

Since it's a two-way communication technique, the test modules also have to make the request
for it to work, like this little code snippet shows:

``` py linenums="1" hl_lines="3"
import pytest

pytestmark = pytest.mark.test_data(__name__.rsplit('.')[-1])
```

The highlighted part is what does that; it calls the fixture with the name of itself (the test
file name) without the file extension.

Also, by using the pytestmark parameter like this, you don't have to add the fixture
to every test case; it's automatically done for you.

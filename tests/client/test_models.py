import pytest

from cnct.client.models import NS


def test_ns_no_specs():
    with pytest.raises(AttributeError) as cv:
        NS(None, None).test_collection

    assert str(cv.value) == 'No specs available. Use the `collection` method instead.'

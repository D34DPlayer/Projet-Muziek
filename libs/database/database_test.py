from . import DBMuziek
import os
# import pytest


def test_database():
    # DATABASE START
    db = DBMuziek("./temp.db")
    db.connect()

    assert db.connection is not None

    # TABLE VALIDATION
    assert db.validate_tables() is False

    assert db.validate_tables() is True

    # DATABASE END
    db.disconnect()

    os.remove("./temp.db")

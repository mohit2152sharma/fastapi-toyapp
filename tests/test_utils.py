import os

import pytest

from app.utils import get_env_var, read_db


def test_read_db():
    db = read_db()
    assert "monte" in db
    assert db["monte"]["username"] == "monte"


class TestGetEnvVar:
    def test_env_var(self, mocker):
        mocker.patch.dict(os.environ, {"SECRET_KEY": "some-key"})
        assert get_env_var("SECRET_KEY") == "some-key"

    def test_raise_error(self):
        with pytest.raises(ValueError):
            get_env_var("SECRET_KEY")

from typing import Dict

import pytest
from httpx import AsyncClient

from app.main import app, get_current_user
from app.models import User


async def override_current_user() -> Dict:
    return User(username="test_user", display_name="Test User", email="test@abc.com")


app.dependency_overrides[get_current_user] = override_current_user


@pytest.mark.anyio
async def test_read_sentence():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/array?sentence=hello world&n=10")
    assert response.status_code == 200
    resp_dict = response.json()
    array = resp_dict["array"]
    user = resp_dict["user"]
    user_name = user["username"]
    display_name = user["display_name"]
    email = user["emailid"]
    assert len(array) == 10
    assert user_name == "test_user"
    assert display_name == "Test User"
    assert email == "test@abc.com"

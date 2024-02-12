import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select


# @pytest.mark.asyncio
async def test_registration(ac: AsyncClient):
    data = {
        "username": "nurlan",
        "password": "123456"
    }
    response = await ac.post(url="/auth/registration", json=data)

    assert response.status_code == 201


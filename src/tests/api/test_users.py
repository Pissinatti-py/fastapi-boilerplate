import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_db_session_connection(db_session):
    """
    Ensure DB session is connected and functional.
    """
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar()

    assert value == 1, "Database session is not functioning correctly."


# @pytest.mark.asyncio
# async def test_pytest():
#     assert 1 == 1


# @pytest.mark.asyncio
# async def test_create_user(client: AsyncClient):
#     payload = {
#         "username": "newuser",
#         "email": "newuser@example.com",
#         "password": "password123",
#         "name": "New User",
#         "is_active": True,
#         "is_superuser": False,
#     }
#     response = await client.post("/api/v1/users/", json=payload)
#     assert response.status_code == 201
#     data = response.json()
#     assert data["username"] == "newuser"
#     assert data["email"] == "newuser@example.com"
#     assert data["is_active"] is True


# @pytest.mark.asyncio
# async def test_get_user(client: AsyncClient, default_user):
#     response = await client.get(f"/api/v1/users/{default_user.id}")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["username"] == default_user.username
#     assert data["email"] == default_user.email


# @pytest.mark.asyncio
# async def test_list_users(client: AsyncClient, default_user):
#     response = await client.get("/api/v1/users/")
#     assert response.status_code == 200
#     data = response.json()
#     assert isinstance(data, list)
#     assert any(user["email"] == default_user.email for user in data)


# @pytest.mark.asyncio
# async def test_delete_user(client: AsyncClient, default_user):
#     response = await client.delete(f"/api/v1/users/{default_user.id}")
#     assert response.status_code == 204

#     check = await client.get(f"/api/v1/users/{default_user.id}")
#     assert check.status_code == 404

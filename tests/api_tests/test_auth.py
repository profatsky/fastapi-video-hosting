import pytest


class TestSignUp:
    @pytest.mark.anyio
    async def test_user_create(self, client, user_to_create):
        resp = await client.post(
            "/auth/sign-up",
            json=user_to_create.dict()
        )
        assert resp.status_code == 201

    @pytest.mark.anyio
    async def test_user_create_twice(self, client, user_to_create):
        await client.post(
            "/auth/sign-up",
            json=user_to_create.dict()
         )
        resp = await client.post(
            "/auth/sign-up",
            json=user_to_create.dict()
        )
        assert resp.status_code == 409
        assert resp.json()["detail"] == "User with this email already exists"


class TestSignIn:
    @pytest.mark.anyio
    async def test_success_login(self, client, user_to_create):
        user_data = user_to_create.dict()
        await client.post(
            "/auth/sign-up",
            json=user_data
        )
        resp = await client.post(
            "/auth/sign-in",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            }
        )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_not_valid_credentials(self, client, user_to_create):
        await client.post(
            "/auth/sign-up",
            json=user_to_create.dict()
        )
        resp = await client.post(
            "/auth/sign-in",
            data={
                "username": "admin@admin.com",
                "password": "qwerty123"
            }
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Could not validate credentials"

import pytest


class TestGetUserInfo:
    @pytest.mark.anyio
    async def test_success_get_user_info(self, client, authorized_client_token, user_to_create):
        resp = await client.get(
            "/users/1"
        )
        assert resp.status_code == 200
        assert resp.json()["username"] == user_to_create.username

    @pytest.mark.anyio
    async def test_get_not_existing_user_info(self, client):
        resp = await client.get(
            "/users/999"
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User doesn't exist"


class TestUpdateUserInfo:
    @pytest.mark.anyio
    async def test_success_update_user_info(self, client):
        await client.post(
            "/auth/sign-up",
            json={
                "username": "user",
                "email": "user@test.com",
                "password": "qwerty"
            }
        )
        resp = await client.post(
            "/auth/sign-in",
            data={
                "username": "user@test.com",
                "password": "qwerty"
            }
        )
        resp = await client.patch(
            "/users/1",
            json={
                "username": "new username",
                "bio": "new bio"
            },
            headers={"Authorization": f"Bearer {resp.json()['access_token']}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "new username"
        assert data["bio"] == "new bio"

    @pytest.mark.anyio
    async def test_update_foreign_user_info(self, client, authorized_client_token):
        await client.post(
            "/auth/sign-up",
            json={
                "email": "second@test.com",
                "username": "second user",
                "password": "qwerty"
            }
        )
        resp = await client.post(
            "/auth/sign-in",
            data={
                "username": "second@test.com",
                "password": "qwerty"
            }
        )
        new_client_token = resp.json()["access_token"]

        resp = await client.patch(
            "/users/1",
            json={
                "username": "new username",
                "bio": "new bio"
            },
            headers={"Authorization": f"Bearer {new_client_token}"}
        )
        assert resp.status_code == 403
        assert resp.json()["detail"] == "Don't have permission"

    @pytest.mark.anyio
    async def test_update_not_existing_user_info(self, client, authorized_client_token):
        resp = await client.patch(
            "/users/999",
            json={
                "username": "new username",
                "bio": "new bio"
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User doesn't exist"

    @pytest.mark.anyio
    async def test_update_user_info_by_unauthorized_user(self, client, authorized_client_token):
        resp = await client.patch(
            "/users/1",
            json={
                "username": "new username",
                "bio": "new bio"
            }
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"


class TestGetUserVideos:
    @pytest.mark.anyio
    async def test_success_get_user_videos(self, client, authorized_client_token, video_file):
        resp = await client.get(
            "/users/1/videos"
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0

        resp = await client.post(
            "/videos/upload",
            data={
                "title": "Test video",
                "description": "Test description"
            },
            files=video_file,
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        video_id = resp.json()["id"]

        resp = await client.get(
            "/users/1/videos"
        )
        await client.delete(
            f"/videos/{video_id}",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == video_id

    @pytest.mark.anyio
    async def test_get_not_existing_user_videos(self, client):
        resp = await client.get(
            "/users/999/videos"
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User doesn't exist"


class TestSubscribeToUser:
    @pytest.mark.anyio
    async def test_success_subscribe(self, client, authorized_client_token):
        await client.post(
            "/auth/sign-up",
            json={
                "email": "second@test.com",
                "username": "second user",
                "password": "qwerty"
            }
        )
        resp = await client.post(
            "/auth/sign-in",
            data={
                "username": "second@test.com",
                "password": "qwerty"
            }
        )
        new_client_token = resp.json()["access_token"]

        resp = await client.put(
            "/users/1/subscribers",
            headers={"Authorization": f"Bearer {new_client_token}"}
        )
        assert resp.status_code == 200
        resp = await client.get(
            "/users/1/subscribers"
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @pytest.mark.anyio
    async def test_subscribe_to_not_existing_user(self, client, authorized_client_token):
        resp = await client.put(
            "/users/999/subscribers",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User doesn't exist"

    @pytest.mark.anyio
    async def test_subscribe_by_unauthorized_user(self, client, authorized_client_token):
        resp = await client.put(
            "/users/1/subscribers",
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_subscribe_to_user_twice(self, client, authorized_client_token):
        await client.post(
            "/auth/sign-up",
            json={
                "email": "second@test.com",
                "username": "second user",
                "password": "qwerty"
            }
        )
        resp = await client.post(
            "/auth/sign-in",
            data={
                "username": "second@test.com",
                "password": "qwerty"
            }
        )
        new_client_token = resp.json()["access_token"]

        first_resp = await client.put(
            "/users/1/subscribers",
            headers={"Authorization": f"Bearer {new_client_token}"}
        )
        assert first_resp.status_code == 200

        second_resp = await client.put(
            "/users/1/subscribers",
            headers={"Authorization": f"Bearer {new_client_token}"}
        )
        assert second_resp.status_code == 200

        resp = await client.get(
            "/users/1/subscribers"
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @pytest.mark.anyio
    async def test_subscribe_on_yourself(self, client, authorized_client_token):
        resp = await client.put(
            "/users/1/subscribers",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 405
        assert resp.json()["detail"] == "You can't subscribe to yourself"


class TestUnsubscribeFromUser:
    @pytest.mark.anyio
    async def test_success_unsubscribe(self, client, authorized_client_token):
        await client.post(
            "/auth/sign-up",
            json={
                "email": "second@test.com",
                "username": "second user",
                "password": "qwerty"
            }
        )
        resp = await client.post(
            "/auth/sign-in",
            data={
                "username": "second@test.com",
                "password": "qwerty"
            }
        )
        new_client_token = resp.json()["access_token"]

        await client.put(
            "/users/1/subscribers",
            headers={"Authorization": f"Bearer {new_client_token}"}
        )
        resp = await client.delete(
            "/users/1/subscribers",
            headers={"Authorization": f"Bearer {new_client_token}"}
        )
        assert resp.status_code == 200

        resp = await client.get(
            "/users/1/subscribers"
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    @pytest.mark.anyio
    async def test_unsubscribe_from_not_existing_user(self, client, authorized_client_token):
        resp = await client.delete(
            "/users/999/subscribers",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User doesn't exist"

    @pytest.mark.anyio
    async def test_unsubscribe_by_unauthorized_user(self, client, authorized_client_token):
        resp = await client.delete(
            "/users/1/subscribers",
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_unsubscribe_without_subscribing(self, client, authorized_client_token):
        await client.post(
            "/auth/sign-up",
            json={
                "email": "second@test.com",
                "username": "second user",
                "password": "qwerty"
            }
        )
        resp = await client.post(
            "/auth/sign-in",
            data={
                "username": "second@test.com",
                "password": "qwerty"
            }
        )
        new_client_token = resp.json()["access_token"]

        resp = await client.delete(
            "/users/1/subscribers",
            headers={"Authorization": f"Bearer {new_client_token}"}
        )
        assert resp.status_code == 200

        resp = await client.get(
            "/users/1/subscribers"
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    @pytest.mark.anyio
    async def test_unsubscribe_from_yourself(self, client, authorized_client_token):
        resp = await client.delete(
            "/users/1/subscribers",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 405
        assert resp.json()["detail"] == "You can't unsubscribe from yourself"


class TestGetUserSubscribers:
    @pytest.mark.anyio
    async def test_success_get_user_subscribers(self, client, authorized_client_token):
        resp = await client.get(
            "/users/1/subscribers"
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0

        await client.post(
            "/auth/sign-up",
            json={
                "email": "second@test.com",
                "username": "second user",
                "password": "qwerty"
            }
        )
        resp = await client.post(
            "/auth/sign-in",
            data={
                "username": "second@test.com",
                "password": "qwerty"
            }
        )
        new_client_token = resp.json()["access_token"]

        await client.put(
            "/users/1/subscribers",
            headers={"Authorization": f"Bearer {new_client_token}"}
        )

        resp = await client.get(
            "/users/1/subscribers"
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @pytest.mark.anyio
    async def test_get_subscribers_of_not_existing_users(self, client):
        resp = await client.get(
            "/users/999/subscribers"
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User doesn't exist"


class TestGetUserSubscriptions:
    @pytest.mark.anyio
    async def test_success_get_user_subscriptions(self, client, authorized_client_token):
        resp = await client.get(
            "/users/1/subscriptions"
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0

        await client.post(
            "/auth/sign-up",
            json={
                "email": "second@test.com",
                "username": "second user",
                "password": "qwerty"
            }
        )
        resp = await client.post(
            "/auth/sign-in",
            data={
                "username": "second@test.com",
                "password": "qwerty"
            }
        )
        new_client_token = resp.json()["access_token"]

        await client.put(
            "/users/1/subscribers",
            headers={"Authorization": f"Bearer {new_client_token}"}
        )

        resp = await client.get(
            "/users/2/subscriptions"
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @pytest.mark.anyio
    async def test_get_subscriptions_of_not_existing_users(self, client):
        resp = await client.get(
            "/users/999/subscriptions"
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User doesn't exist"

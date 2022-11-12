import os

import pytest


class TestUploadVideo:
    @pytest.mark.anyio
    async def test_success_upload_video(self, client, authorized_client_token, video_file):
        resp = await client.post(
            "/videos/upload",
            data={
                "title": "test video",
                "description": "test description"
            },
            files=video_file,
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        await client.delete(
            f"/videos/{resp.json()['id']}",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "test video"
        assert data["description"] == "test description"
        assert data["author"]["username"] == "test"

    @pytest.mark.anyio
    async def test_upload_video_by_unauthorized_user(self, client, video_file):
        resp = await client.post(
            "/videos/upload",
            data={
                "title": "Test video",
                "description": "Test description"
            },
            files=video_file
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_upload_not_video(self, client, authorized_client_token):
        txt_file = {
            'file': (
                "test.txt",
                open(os.path.dirname(__file__).replace("api_tests", "assets/test.txt"), "rb"),
                "text/plain"
            )
        }
        resp = await client.post(
            "/videos/upload",
            data={
                "title": "test video",
                "description": "test description"
            },
            files=txt_file,
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 415
        assert resp.json()["detail"] == "File type must be mp4"


class TestDeleteVideo:
    @pytest.mark.anyio
    async def test_success_delete_video(self, client, authorized_client_token, video_file):
        resp = await client.post(
            "/videos/upload",
            data={
                "title": "Test video",
                "description": "Test description"
            },
            files=video_file,
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        resp = await client.delete(
            f"/videos/{resp.json()['id']}",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 204

    @pytest.mark.anyio
    async def test_delete_video_by_unauthorized_user(self, client, authorized_client_token, video_file):
        video_resp = await client.post(
            "/videos/upload",
            data={
                "title": "Test video",
                "description": "Test description"
            },
            files=video_file,
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        resp = await client.delete(
            f"/videos/{video_resp.json()['id']}",
        )
        await client.delete(
            f"/videos/{video_resp.json()['id']}",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_delete_not_existing_video(self, client, authorized_client_token):
        resp = await client.delete(
            f"/videos/999",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 404
        assert resp.json()['detail'] == "Video doesn't exist"

    @pytest.mark.anyio
    async def test_delete_foreign_video(self, client, authorized_client_token, video_file):
        # Upload new video by authed user
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
        # Create new user
        await client.post(
            "/auth/sign-up",
            json={
                "email": "second@test.com",
                "username": "second_user",
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

        # Try to delete video by new user
        resp = await client.delete(
            f"/videos/{video_id}",
            headers={"Authorization": f"Bearer {new_client_token}"}
        )

        await client.delete(
            f"/videos/{video_id}",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )

        assert resp.status_code == 403
        assert resp.json()["detail"] == "Don't have permission"


class TestGetVideo:
    @pytest.mark.anyio
    async def test_get_video(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.get(
            f"/videos/{uploaded_video_id}"
        )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_get_not_existing_video(self, client):
        resp = await client.get(f"/videos/999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Video doesn't exist"


class TestGetStreamingVideo:
    # @pytest.mark.anyio
    # async def test_get_streaming_video(self, client, authorized_client_token, uploaded_video_id):
    #     resp = await client.get(
    #         f"/videos/{uploaded_video_id}/watching"
    #     )
    #     assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_get_streaming_not_existing_video(self, client):
        resp = await client.get(
            f"/videos/999/watching"
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Video doesn't exist"


class TestUpdateVideo:
    @pytest.mark.anyio
    async def test_success_update_video(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.patch(
            f"/videos/{uploaded_video_id}",
            json={
                "title": "new title",
                "description": "new description"
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "new title"
        assert resp.json()["description"] == "new description"

    @pytest.mark.anyio
    async def test_update_video_by_by_unauthorized_user(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.patch(
            f"/videos/{uploaded_video_id}",
            json={
                "title": "new title",
                "description": "new description"
            }
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_update_foreign_video(self, client, authorized_client_token, uploaded_video_id):
        await client.post(
            "/auth/sign-up",
            json={
                "email": "second@test.com",
                "username": "second_user",
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

        # Try to update video by new user
        resp = await client.patch(
            f"/videos/{uploaded_video_id}",
            json={
                "title": "new title",
                "description": "new description"
            },
            headers={"Authorization": f"Bearer {new_client_token}"}
        )
        assert resp.status_code == 403
        assert resp.json()["detail"] == "Don't have permission"

    @pytest.mark.anyio
    async def test_update_not_existing_video(self, client, authorized_client_token):
        resp = await client.patch(
            f"/videos/999",
            json={
                "title": "new title",
                "description": "new description"
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Video doesn't exist"


class TestGetVideoLikes:
    @pytest.mark.anyio
    async def test_success_get_likes(self, client, authorized_client_token, uploaded_video_id):
        await client.put(
            f"/videos/{uploaded_video_id}/likes",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        resp = await client.get(
            f"/videos/{uploaded_video_id}/likes"
        )
        assert resp.status_code == 200
        assert resp.json() == [{"username": "test", "id": 1}]

    @pytest.mark.anyio
    async def test_get_not_existing_video_likes(self, client):
        resp = await client.get(
            f"/videos/999/likes"
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Video doesn't exist"


class TestLikeVideo:
    @pytest.mark.anyio
    async def test_success_like_video(self, client, authorized_client_token, uploaded_video_id):
        like_resp = await client.put(
            f"/videos/{uploaded_video_id}/likes",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        get_likes_resp = await client.get(
            f"/videos/{uploaded_video_id}/likes"
        )
        assert like_resp.status_code == 200
        assert get_likes_resp.json() == [{"username": "test", "id": 1}]

    @pytest.mark.anyio
    async def test_like_not_existing_video(self, client, authorized_client_token):
        resp = await client.put(
            f"/videos/999/likes",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Video doesn't exist"

    @pytest.mark.anyio
    async def test_like_video_by_unauthorized_user(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.put(
            f"/videos/{uploaded_video_id}/likes"
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_like_video_twice(self, client, authorized_client_token, uploaded_video_id):
        await client.put(
            f"/videos/{uploaded_video_id}/likes",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        like_resp = await client.put(
            f"/videos/{uploaded_video_id}/likes",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        get_likes_resp = await client.get(
            f"/videos/{uploaded_video_id}/likes"
        )
        assert like_resp.status_code == 200
        assert get_likes_resp.json() == [{"username": "test", "id": 1}]


class TestUnlikeVideo:
    @pytest.mark.anyio
    async def test_success_unlike_video(self, client, authorized_client_token, uploaded_video_id):
        await client.put(
            f"/videos/{uploaded_video_id}/likes",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        unlike_resp = await client.delete(
            f"videos/{uploaded_video_id}/likes",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        get_likes_resp = await client.get(
            f"/videos/{uploaded_video_id}/likes"
        )
        assert unlike_resp.status_code == 200
        assert get_likes_resp.json() == []

    @pytest.mark.anyio
    async def test_unlike_not_existing_video(self, client, authorized_client_token):
        resp = await client.delete(
            f"videos/999/likes",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Video doesn't exist"

    @pytest.mark.anyio
    async def test_unlike_video_by_unauthorized_user(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.delete(
            f"/videos/{uploaded_video_id}/likes"
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_unlike_video_without_liking(self, client, authorized_client_token, uploaded_video_id):
        unlike_resp = await client.delete(
            f"/videos/{uploaded_video_id}/likes",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        get_likes_resp = await client.get(
            f"/videos/{uploaded_video_id}/likes"
        )
        assert unlike_resp.status_code == 200
        assert get_likes_resp.json() == []

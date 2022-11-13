import pytest


class TestLeaveComment:
    @pytest.mark.anyio
    async def test_success_leave_comment(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.post(
            f"/videos/{uploaded_video_id}/comments",
            json={
                "text": "test comment",
                "answer_to": 0
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["text"] == "test comment"
        assert data["answer_to"] is None
        assert data["author"] == {"username": "test", "id": 1}

    @pytest.mark.anyio
    async def test_leave_comment_by_unauthorized_user(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.post(
            f"/videos/{uploaded_video_id}/comments",
            json={
                "text": "test comment",
                "answer_to": 0
            }
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_leave_comment_on_not_existing_video(self, client, authorized_client_token):
        resp = await client.post(
            f"/videos/999/comments",
            json={
                "text": "test comment",
                "answer_to": 0
            }
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Video doesn't exist"


class TestDeleteComment:
    @pytest.mark.anyio
    async def test_success_delete_comment(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.post(
            f"/videos/{uploaded_video_id}/comments",
            json={
                "text": "test comment",
                "answer_to": 0
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        resp = await client.delete(
            f"/videos/{uploaded_video_id}/comments/{resp.json()['id']}",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 204

    @pytest.mark.anyio
    async def test_delete_comment_by_unauthorized_user(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.post(
            f"/videos/{uploaded_video_id}/comments",
            json={
                "text": "test comment",
                "answer_to": 0
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        resp = await client.delete(
            f"/videos/{uploaded_video_id}/comments/{resp.json()['id']}"
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_delete_comment_on_not_existing_video(self, client, authorized_client_token):
        resp = await client.delete(
            f"/videos/999/comments/999",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Video doesn't exist"

    @pytest.mark.anyio
    async def test_delete_not_existing_comment(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.delete(
            f"/videos/{uploaded_video_id}/comments/999",
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Comment doesn't exist"

    @pytest.mark.anyio
    async def test_delete_foreign_comment(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.post(
            f"/videos/{uploaded_video_id}/comments",
            json={
                "text": "test comment",
                "answer_to": 0
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        comment_id = resp.json()["id"]

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

        resp = await client.delete(
            f"/videos/{uploaded_video_id}/comments/{comment_id}",
            headers={"Authorization": f"Bearer {new_client_token}"}
        )
        assert resp.status_code == 403
        assert resp.json()["detail"] == "Don't have permission"


class TestGetComment:
    @pytest.mark.anyio
    async def test_success_get_comment(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.post(
            f"/videos/{uploaded_video_id}/comments",
            json={
                "text": "test comment",
                "answer_to": 0
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        left_comment = resp.json()
        resp = await client.get(
            f"/videos/{uploaded_video_id}/comments/{left_comment['id']}"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["text"] == left_comment["text"]
        assert data["answer_to"] == left_comment["answer_to"]
        assert data["author"] == left_comment["author"]

    @pytest.mark.anyio
    async def test_get_comment_on_not_existing_video(self, client, authorized_client_token):
        resp = await client.get(
            f"/videos/999/comments/999"
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Video doesn't exist"

    @pytest.mark.anyio
    async def test_get_not_existing_comment(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.get(
            f"/videos/{uploaded_video_id}/comments/999"
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Comment doesn't exist"


class TestGetListComments:
    @pytest.mark.anyio
    async def test_success_get_list_comments(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.get(
            f"/videos/{uploaded_video_id}/comments"
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0

        resp = await client.post(
            f"/videos/{uploaded_video_id}/comments",
            json={
                "text": "test comment",
                "answer_to": 0
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        left_comment = resp.json()

        resp = await client.get(
            f"/videos/{uploaded_video_id}/comments"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["text"] == left_comment["text"]
        assert data[0]["author"] == left_comment["author"]

    @pytest.mark.anyio
    async def test_get_list_comments_on_not_existing_video(self, client):
        resp = await client.get(
            f"/videos/999/comments"
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Video doesn't exist"


class TestUpdateComment:
    @pytest.mark.anyio
    async def test_success_update_comment(self, client, authorized_client_token, uploaded_video_id):
        comment_resp = await client.post(
            f"/videos/{uploaded_video_id}/comments",
            json={
                "text": "test comment",
                "answer_to": 0
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        resp = await client.patch(
            f"/videos/{uploaded_video_id}/comments/{comment_resp.json()['id']}",
            json={
                "text": "updated comment"
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 200
        assert resp.json()["text"] == "updated comment"

    @pytest.mark.anyio
    async def test_update_comment_on_not_existing_video(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.patch(
            f"/videos/999/comments/999",
            json={
                "text": "updated comment"
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Video doesn't exist"

    @pytest.mark.anyio
    async def test_update_not_existing_comment(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.patch(
            f"/videos/{uploaded_video_id}/comments/999",
            json={
                "text": "updated comment"
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Comment doesn't exist"

    @pytest.mark.anyio
    async def test_update_foreign_comment(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.post(
            f"/videos/{uploaded_video_id}/comments",
            json={
                "text": "test comment",
                "answer_to": 0
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        comment_id = resp.json()["id"]

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

        resp = await client.patch(
            f"/videos/{uploaded_video_id}/comments/{comment_id}",
            json={
                "text": "updated comment"
            },
            headers={"Authorization": f"Bearer {new_client_token}"}
        )
        assert resp.status_code == 403
        assert resp.json()["detail"] == "Don't have permission"

    @pytest.mark.anyio
    async def test_update_comment_by_unauthorized_user(self, client, authorized_client_token, uploaded_video_id):
        resp = await client.post(
            f"/videos/{uploaded_video_id}/comments",
            json={
                "text": "test comment",
                "answer_to": 0
            },
            headers={"Authorization": f"Bearer {authorized_client_token}"}
        )
        comment_id = resp.json()["id"]

        resp = await client.patch(
            f"/videos/{uploaded_video_id}/comments/{comment_id}",
            json={
                "text": "updated comment"
            }
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"

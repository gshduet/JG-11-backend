import pytest

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.fixture
def user_token(client):
    """테스트용 사용자를 등록하고 로그인하여 토큰을 반환하는 픽스처입니다."""
    signup_data = {
        "email": "testuser@example.com",
        "password": "testpassword",
        "password_check": "testpassword",
        "user_name": "테스트유저",
    }
    client.post("/api/users/signup", json=signup_data)

    login_data = {"email": signup_data["email"], "password": signup_data["password"]}
    response = client.post("/api/users/login", json=login_data)
    return response.cookies.get("access_token")


@pytest.fixture
def test_post(client, user_token):
    """테스트용 게시글을 생성하고 해당 게시글의 정보를 반환하는 픽스처입니다."""
    client.cookies.set("access_token", user_token)
    post_data = {"title": "테스트 게시글", "content": "테스트 내용입니다."}
    response = client.post("/api/posts", json=post_data)
    return response.json()


@pytest.fixture
def test_comment(client, user_token, test_post):
    """테스트용 댓글을 생성하고 해당 댓글의 정보를 반환하는 픽스처입니다."""
    client.cookies.set("access_token", user_token)
    comment_data = {"content": "테스트 댓글입니다."}
    response = client.post(f"/api/comments?post_id={test_post['id']}", json=comment_data)
    return response.json()


def test_create_comment_success(client, user_token, test_post):
    """댓글 작성 성공 시나리오를 테스트합니다."""
    client.cookies.set("access_token", user_token)
    
    comment_data = {
        "content": "테스트 댓글입니다."
    }
    response = client.post(f"/api/comments?post_id={test_post['id']}", json=comment_data)
    assert response.status_code == 201
    assert response.json()["content"] == comment_data["content"]
    assert response.json()["post_id"] == test_post["id"]


def test_create_comment_unauthorized(client, test_post):
    """인증되지 않은 사용자의 댓글 작성 시도를 테스트합니다."""
    client.cookies.clear()
    
    comment_data = {"content": "테스트 댓글입니다."}
    response = client.post(f"/api/comments?post_id={test_post['id']}", json=comment_data)
    assert response.status_code == 401


def test_get_comments(client, test_post, test_comment):
    """댓글 목록 조회를 테스트합니다."""
    response = client.get(f"/api/comments?post_id={test_post['id']}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["content"] == test_comment["content"]


def test_update_comment_success(client, user_token, test_post, test_comment):
    """댓글 수정 성공 시나리오를 테스트합니다."""
    client.cookies.set("access_token", user_token)
    
    update_data = {"content": "수정된 댓글입니다."}
    response = client.patch(
        f"/api/comments/{test_comment['id']}?post_id={test_post['id']}", 
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["content"] == update_data["content"]


def test_update_comment_unauthorized(client, test_post, test_comment):
    """인증되지 않은 사용자의 댓글 수정 시도를 테스트합니다."""
    client.cookies.clear()
    
    update_data = {"content": "수정된 댓글입니다."}
    response = client.patch(
        f"/api/comments/{test_comment['id']}?post_id={test_post['id']}", 
        json=update_data
    )
    assert response.status_code == 401


def test_delete_comment_success(client, user_token, test_post, test_comment):
    """댓글 삭제 성공 시나리오를 테스트합니다."""
    client.cookies.set("access_token", user_token)
    
    response = client.delete(
        f"/api/comments/{test_comment['id']}?post_id={test_post['id']}"
    )
    assert response.status_code == 204

    # 삭제된 댓글 조회 시도
    get_response = client.get(f"/api/comments?post_id={test_post['id']}")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0


def test_delete_comment_unauthorized(client, test_post, test_comment):
    """인증되지 않은 사용자의 댓글 삭제 시도를 테스트합니다."""
    client.cookies.clear()
    
    response = client.delete(
        f"/api/comments/{test_comment['id']}?post_id={test_post['id']}"
    )
    assert response.status_code == 401

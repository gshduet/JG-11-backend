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
        "user_name": "테스트유저"
    }
    client.post("/api/users/signup", json=signup_data)
    
    login_data = {
        "email": signup_data["email"],
        "password": signup_data["password"]
    }
    response = client.post("/api/users/login", json=login_data)
    return response.cookies.get("access_token")


@pytest.fixture
def test_post(client, user_token):
    """테스트용 게시글을 생성하고 해당 게시글의 정보를 반환하는 픽스처입니다."""
    client.cookies.set("access_token", user_token)
    post_data = {
        "title": "테스트 게시글",
        "content": "테스트 내용입니다."
    }
    response = client.post("/api/posts", json=post_data)
    return response.json()


def test_create_post_success(client, user_token):
    """게시글 작성 성공 시나리오를 테스트합니다."""
    client.cookies.set("access_token", user_token)
    
    post_data = {
        "title": "테스트 게시글",
        "content": "테스트 내용입니다."
    }
    response = client.post("/api/posts", json=post_data)
    assert response.status_code == 201
    assert response.json()["title"] == post_data["title"]
    assert response.json()["content"] == post_data["content"]


def test_create_post_unauthorized(client):
    """인증되지 않은 사용자의 게시글 작성 시도를 테스트합니다."""
    post_data = {"title": "테스트 게시글", "content": "테스트 내용입니다."}
    response = client.post("/api/posts", json=post_data)
    assert response.status_code == 401
    assert "detail" in response.json()


def test_get_posts(client, test_post):
    """게시글 목록 조회를 테스트합니다."""
    response = client.get("/api/posts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["title"] == test_post["title"]


def test_get_post_by_id(client, test_post):
    """특정 게시글 조회를 테스트합니다."""
    response = client.get(f"/api/posts/{test_post['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == test_post["title"]
    assert response.json()["content"] == test_post["content"]


def test_get_nonexistent_post(client):
    """존재하지 않는 게시글 ��회를 테스트합니다."""
    response = client.get("/api/posts/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "게시글을 찾을 수 없습니다."


def test_update_post_success(client, user_token, test_post):
    """게시글 수정 성공 시나리오를 테스트합니다."""
    client.cookies.set("access_token", user_token)
    
    update_data = {"title": "수정된 제목", "content": "수정된 내용입니다."}
    response = client.patch(f"/api/posts/{test_post['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]
    assert response.json()["content"] == update_data["content"]


def test_update_post_unauthorized(client, test_post):
    """인증되지 않은 사용자의 게시글 수정 시도를 테스트합니다."""
    client.cookies.clear()
    
    update_data = {"title": "수정된 제목", "content": "수정된 내용입니다."}
    response = client.patch(f"/api/posts/{test_post['id']}", json=update_data)
    assert response.status_code == 401


def test_delete_post_success(client, user_token, test_post):
    """게시글 삭제 성공 시나리오를 테스트합니다."""
    client.cookies.set("access_token", user_token)
    
    response = client.delete(f"/api/posts/{test_post['id']}")
    assert response.status_code == 204

    # 삭제된 게시글 조회 시도
    get_response = client.get(f"/api/posts/{test_post['id']}")
    assert get_response.status_code == 404


def test_delete_post_unauthorized(client, test_post):
    """인증되지 않은 사용자의 게시글 삭제 시도를 테스트합니다."""
    client.cookies.clear()
    
    response = client.delete(f"/api/posts/{test_post['id']}")
    assert response.status_code == 401
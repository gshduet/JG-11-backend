import pytest

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture
def new_user_data():
    """회원가입에 사용할 사용자 데이터를 반환하는 픽스처입니다."""
    return {
        "email": "testuser@example.com",
        "password": "testpassword",
        "password_check": "testpassword",
        "user_name": "테스트유저",
    }


@pytest.fixture
def registered_user(client, new_user_data):
    """테스트용 사용자를 등록하고 로그인 데이터를 반환하는 픽스처입니다."""
    client.post("/api/users/signup", json=new_user_data)
    return {"email": new_user_data["email"], "password": new_user_data["password"]}


def test_signup_success(client, new_user_data):
    """회원가입 성공 시나리오를 테스트합니다."""
    response = client.post("/api/users/signup", json=new_user_data)
    assert response.status_code == 201
    assert response.json() == {"message": "회원가입이 완료되었습니다."}


def test_signup_password_mismatch(client, new_user_data):
    """비밀번호 불일치 시나리오를 테스트합니다."""
    new_user_data["password_check"] = "wrongpassword"
    response = client.post("/api/users/signup", json=new_user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "비밀번호가 일치하지 않습니다."


def test_signup_duplicate_email(client, new_user_data):
    """이메일 중복 시나리오를 테스트합니다."""
    client.post("/api/users/signup", json=new_user_data)
    response = client.post("/api/users/signup", json=new_user_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "이미 등록된 이메일입니다."


def test_login_success(client, registered_user):
    """로그인 성공 시나리오를 테스트합니다."""
    response = client.post("/api/users/login", json=registered_user)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["message"] == "로그인에 성공했습니다."

    # 쿠키를 클라이언트 인스턴스에 직접 설정
    client.cookies.set("access_token", response.cookies.get("access_token"))


def test_login_wrong_password(client, registered_user):
    """잘못된 비밀번호로 로그인 시도하는 시나리오를 테스트합니다."""
    wrong_password_data = registered_user.copy()
    wrong_password_data["password"] = "wrongpassword"
    response = client.post("/api/users/login", json=wrong_password_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다."


def test_login_nonexistent_email(client):
    """존재하지 않는 이메일로 로그인 시도하는 시나리오를 테스트합니다."""
    response = client.post(
        "/api/users/login",
        json={"email": "nonexistent@example.com", "password": "testpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다."


def test_signout_success(client, registered_user):
    """로그아웃 성공 시나리오를 테스트합니다."""
    # 로그인 후 쿠키 설정
    login_response = client.post("/api/users/signin", json=registered_user)
    client.cookies.set("access_token", login_response.cookies.get("access_token"))

    # 로그아웃
    response = client.post("/api/users/signout")
    assert response.status_code == 200
    assert response.json()["message"] == "로그아웃 되었습니다."


def test_signout_without_login(client):
    """로그인하지 않은 상태에서 로그아웃 시도하는 시나리오를 테스트합니다."""
    response = client.post("/api/users/signout")
    assert response.status_code == 200  # 로그아웃은 항상 성공
    assert response.json()["message"] == "로그아웃 되었습니다."

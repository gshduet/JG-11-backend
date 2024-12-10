import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient

from main import app
from core.database import get_session

# 테스트용 인메모리 데이터베이스 설정
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# 테스트용 데이터베이스 세션 생성
@pytest.fixture(scope="function")
def db_session():
    SQLModel.metadata.create_all(bind=engine)  # 테이블 생성
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(bind=engine)  # 테이블 삭제


# FastAPI의 의존성을 테스트용 세션으로 대체
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_session():
        with db_session as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

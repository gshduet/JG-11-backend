from datetime import datetime, timedelta
from typing import Optional, Any

import jwt
import bcrypt
from fastapi import HTTPException, status

from core.config import get_settings

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    일반 비밀번호와 해시된 비밀번호를 비교합니다.
    bcrypt의 checkpw 함수를 사용하여 비밀번호를 검증합니다.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """
    비밀번호를 해시화합니다.
    bcrypt의 기본 설정으로 솔트를 자동 생성하여 해시를 만듭니다.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    JWT 액세스 토큰을 생성합니다.
    PyJWT를 사용하여 토큰을 생성하며, 만료 시간을 포함한 페이로드를 인코딩합니다.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    JWT 토큰을 디코딩합니다.
    토큰이 유효하지 않거나 만료된 경우 예외를 발생시킵니다.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰이 만료되었습니다."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다."
        )

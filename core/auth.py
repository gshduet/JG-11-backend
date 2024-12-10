from typing import Annotated

from fastapi import Depends, HTTPException, status, Cookie
from sqlmodel import Session, select

from core.database import get_session
from core.security import decode_access_token
from models.users import User


async def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_session),
) -> User:
    """
    쿠키에서 access_token을 확인하고 현재 인증된 사용자를 반환하는 의존성 함수입니다.
    토큰이 유효하지 않거나 사용자를 찾을 수 없는 경우 401 에러를 발생시킵니다.
    """
    if not access_token or not access_token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="인증되지 않은 요청입니다."
        )

    try:
        # Bearer 제거하고 토큰만 추출
        token = access_token.split(" ")[1]
        payload = decode_access_token(token)
        user_uuid = payload.get("sub")

        if not user_uuid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 인증 정보입니다.",
            )

        # UUID로 사용자 조회
        user = db.exec(select(User).where(User.uuid == user_uuid)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다.",
            )

        return user

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 처리 중 오류가 발생했습니다.",
        )

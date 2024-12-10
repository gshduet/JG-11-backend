import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from core.database import get_session
from core.security import get_password_hash, verify_password, create_access_token
from core.auth import get_current_user
from models.users import User
from schemas.users import SignUpRequest, SignInRequest

user_router = APIRouter(prefix="/api/users")


@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest, db: Session = Depends(get_session)):
    """
    회원가입을 처리하는 엔드포인트입니다.
    1. 비밀번호 확인
    2. 이메일 중복 확인
    3. 사용자 생성
    """
    # 비밀번호 일치 여부 확인
    if request.password != request.password_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호가 일치하지 않습니다.",
        )

    # 이메일 중복 확인
    existing_user = db.exec(select(User).where(User.email == request.email)).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 등록된 이메일입니다."
        )

    try:
        # 새로운 사용자 생성
        new_user = User(
            email=request.email,
            password=get_password_hash(request.password),
            user_name=request.user_name,
            uuid=str(uuid.uuid4()),
        )

        db.add(new_user)
        db.commit()

        return {"message": "회원가입이 완료되었습니다."}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원가입 처리 중 오류가 발생했습니다.",
        )


@user_router.post("/login")
async def signin(
    request: SignInRequest, response: Response, db: Session = Depends(get_session)
):
    """
    로그인을 처리하는 엔드포인트입니다.
    1. 이메일로 사용자 조회
    2. 비밀번호 검증
    3. 액세스 토큰 생성 및 쿠키 설정
    """
    try:
        # 사용자 조회 및 비밀번호 검증
        user = db.exec(select(User).where(User.email == request.email)).first()

        if not user or not verify_password(request.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            )

        # 액세스 토큰 생성
        access_token = create_access_token(
            data={"sub": user.uuid}, expires_delta=timedelta(hours=1)
        )

        token_value = f"Bearer {access_token}"

        # 쿠키 설정
        response.set_cookie(
            key="access_token",
            value=token_value,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600,
        )

        return {
            "message": "로그인에 성공했습니다.",
            "user_name": user.user_name,
            "access_token": token_value,
        }

    except HTTPException:
        raise  # 401 에러는 그대로 전달

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다.",
        )


@user_router.get("/me")
async def get_my_info(current_user: Annotated[User, Depends(get_current_user)]):
    """
    현재 로그인한 사용자의 정보를 반환하는 엔드포인트입니다.
    """
    return {"email": current_user.email, "user_name": current_user.user_name}


@user_router.post("/signout")
async def signout(response: Response):
    """
    로그아웃을 처리하는 엔드포인트입니다.
    access_token 쿠키를 제거합니다.
    """
    # 쿠키 삭제
    response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="lax")

    return {"message": "로그아웃 되었습니다."}

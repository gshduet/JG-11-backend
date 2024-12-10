from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    """
    회원가입 요청 시 사용되는 스키마입니다.
    이메일, 비밀번호, 사용자명을 필수로 받습니다.
    """

    email: EmailStr
    password: str
    password_check: str
    user_name: str


class SignInRequest(BaseModel):
    """
    로그인 요청 시 사용되는 스키마입니다.
    이메일과 비밀번호만 받습니다.
    """

    email: EmailStr
    password: str


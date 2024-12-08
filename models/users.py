from datetime import datetime
from typing import Optional

from sqlmodel import Field

from models.commons import TimeStamp


class User(TimeStamp, table=True):
    """
    사용자 정보를 저장하는 모델입니다.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password: str
    user_name: str

    # 시스템 필드들
    uuid: str = Field(unique=True, index=True)
    last_login_at: Optional[datetime] = None

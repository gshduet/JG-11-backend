from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class TimeStamp(SQLModel):
    """
    생성 시간과 수정 시간만을 관리하는 기본 클래스입니다.
    """

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )


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


class Post(TimeStamp, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str

    # 외래키 관계
    user_id: int = Field(foreign_key="user.id")

    # 소프트 딜리트 구현
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None


class Comment(TimeStamp, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str

    # 외래키 관계
    user_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="post.id")

    # 소프트 딜리트 구현
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
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


class SoftDelete(SQLModel):
    """
    소프트 딜리트 구현
    """

    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

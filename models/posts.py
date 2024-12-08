from typing import Optional

from sqlmodel import Field

from models.commons import TimeStamp, SoftDelete


class Post(TimeStamp, SoftDelete, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str

    # 외래키 관계
    user_id: int = Field(foreign_key="user.id")


class Comment(TimeStamp, SoftDelete, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str

    # 외래키 관계
    user_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="post.id")

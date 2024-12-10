from pydantic import BaseModel


class CommentCreate(BaseModel):
    """
    댓글 작성 요청에 사용되는 스키마입니다.
    내용만 받습니다.
    """

    content: str


class CommentUpdate(BaseModel):
    """
    댓글 수정 요청에 사용되는 스키마입니다.
    내용만 수정 가능합니다.
    """

    content: str


class CommentResponse(BaseModel):
    """
    댓글 응답에 사용되는 스키마입니다.
    """

    id: int
    content: str
    user_name: str
    post_id: int

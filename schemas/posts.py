from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    """
    게시글 작성 요청에 사용되는 스키마입니다.
    제목과 내용을 필수로 받습니다.
    """

    title: str
    content: str


class PostResponse(BaseModel):
    """
    게시글 응답에 사용되는 스키마입니다.
    """

    id: int
    title: str
    content: str
    user_name: str

    # ConfigDict를 사용하여 설정을 정의합니다.
    model_config = ConfigDict(
        from_attributes=True
    )


class PostUpdate(BaseModel):
    """
    게시글 수정 요청에 사용되는 스키마입니다.
    제목과 내용을 선택적으로 받습니다.
    """

    title: str | None = None
    content: str | None = None

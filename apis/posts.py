from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.database import get_session
from core.auth import get_current_user
from models.posts import Post
from models.users import User
from schemas.posts import PostCreate, PostResponse, PostUpdate

post_router = APIRouter(prefix="/api/posts")


@post_router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: PostCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    """
    새로운 게시글을 작성하는 엔드포인트입니다.
    로그인된 사용자만 접근할 수 있습니다.
    """
    try:
        # 새 게시글 생성
        new_post = Post(
            title=request.title, content=request.content, user_uuid=current_user.uuid
        )

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        # 응답 데이터 구성
        return PostResponse(
            id=new_post.id,
            title=new_post.title,
            content=new_post.content,
            user_name=current_user.user_name,
        )

    except Exception as e:
        print(f"@@@@@@@@@@@ Error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 작성 중 오류가 발생했습니다.",
        )


@post_router.get("", response_model=List[PostResponse])
async def get_posts(db: Session = Depends(get_session), skip: int = 0, limit: int = 10):
    """
    게시글 목록을 조회하는 엔드포인트입니다.
    페이지네이션을 지원하며 누구나 접근 가능합니다.
    """
    try:
        # 삭제되지 않은 게시글만 조회
        posts = db.exec(
            select(Post, User)
            .join(User, Post.user_uuid == User.uuid)
            .where(Post.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(Post.created_at.desc())
        ).all()

        # (Post, User) 튜플을 PostResponse로 변환
        return [
            PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                user_name=user.user_name,
            )
            for post, user in posts
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 목록 조회 중 오류가 발생했습니다.",
        )


@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_session)):
    """
    특정 게시글을 조회하는 엔드포인트입니다.
    게시글 ID를 통해 조회하며 누구나 접근 가능합니다.
    """
    try:
        # 게시글과 작성자 정보를 함께 조회
        result = db.exec(
            select(Post, User)
            .join(User, Post.user_uuid == User.uuid)
            .where(Post.id == post_id, Post.is_deleted == False)
        ).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다.",
            )

        post, user = result

        return PostResponse(
            id=post.id, title=post.title, content=post.content, user_name=user.user_name
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 조회 중 오류가 발생했습니다.",
        )


@post_router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    request: PostUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    """
    게시글을 수정하는 엔드포인트입니다.
    작성자만 수정할 수 있습니다.
    """
    try:
        # 게시글 조회
        post = db.exec(
            select(Post).where(Post.id == post_id, Post.is_deleted == False)
        ).first()

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다.",
            )

        # 작성자 확인
        if post.user_uuid != current_user.uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시글을 수정할 권한이 없습니다.",
            )

        # 수정할 필드만 업데이트
        if request.title is not None:
            post.title = request.title
        if request.content is not None:
            post.content = request.content

        db.add(post)
        db.commit()
        db.refresh(post)

        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            user_name=current_user.user_name,
        )

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 수정 중 오류가 발생했습니다.",
        )


@post_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    """
    게시글을 삭제하는 엔드포인트입니다.
    작성자만 삭제할 수 있으며, 소프트 삭제로 처리됩니다.
    """
    try:
        # 게시글 조회
        post = db.exec(
            select(Post).where(Post.id == post_id, Post.is_deleted == False)
        ).first()

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다.",
            )

        # 작성자 확인
        if post.user_uuid != current_user.uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시글을 삭제할 권한이 없습니다.",
            )

        # 소프트 삭제 처리
        post.soft_delete()

        db.add(post)
        db.commit()

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 삭제 중 오류가 발생했습니다.",
        )

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.database import get_session
from core.auth import get_current_user
from models.posts import Comment, Post
from models.users import User
from schemas.comments import CommentCreate, CommentUpdate, CommentResponse

comment_router = APIRouter(prefix="/api/comments")


@comment_router.post(
    "", response_model=CommentResponse, status_code=status.HTTP_201_CREATED
)
async def create_comment(
    post_id: int,
    request: CommentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    """
    댓글을 작성하는 엔드포인트입니다.
    로그인한 사용자만 작성할 수 있습니다.
    """
    try:
        # 게시글 존재 여부 확인
        post = db.exec(
            select(Post).where(Post.id == post_id, Post.is_deleted == False)
        ).first()

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다.",
            )

        # 새 댓글 생성
        new_comment = Comment(
            content=request.content, user_uuid=current_user.uuid, post_id=post_id
        )

        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)

        return CommentResponse(
            id=new_comment.id,
            content=new_comment.content,
            user_name=current_user.user_name,
            post_id=post_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 작성 중 오류가 발생했습니다.",
        )


@comment_router.get("", response_model=List[CommentResponse])
async def get_comments(
    post_id: int, db: Session = Depends(get_session), skip: int = 0, limit: int = 50
):
    """
    특정 게시글의 댓글 목록을 조회하는 엔드포인트입니다.
    누구나 조회할 수 있습니다.
    """
    try:
        # 게시글 존재 여부 확인
        post = db.exec(
            select(Post).where(Post.id == post_id, Post.is_deleted == False)
        ).first()

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다.",
            )

        # 댓글 목록 조회
        comments = db.exec(
            select(Comment, User)
            .join(User, Comment.user_uuid == User.uuid)
            .where(Comment.post_id == post_id, Comment.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(Comment.created_at.desc())
        ).all()

        return [
            CommentResponse(
                id=comment.id,
                content=comment.content,
                user_name=user.user_name,
                post_id=post_id,
            )
            for comment, user in comments
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 목록 조회 중 오류가 발생했습니다.",
        )


@comment_router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    post_id: int,
    comment_id: int,
    request: CommentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    """
    댓글을 수정하는 엔드포인트입니다.
    작성자만 수정할 수 있습니다.
    """
    try:
        # 댓글 조회
        comment = db.exec(
            select(Comment).where(
                Comment.id == comment_id,
                Comment.post_id == post_id,
                Comment.is_deleted == False,
            )
        ).first()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="댓글을 찾을 수 없습니다."
            )

        # 작성자 확인
        if comment.user_uuid != current_user.uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="댓글을 수정할 권한이 없습니다.",
            )

        # 댓글 수정
        comment.content = request.content

        db.add(comment)
        db.commit()
        db.refresh(comment)

        return CommentResponse(
            id=comment.id,
            content=comment.content,
            user_name=current_user.user_name,
            post_id=post_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 수정 중 오류가 발생했습니다.",
        )


@comment_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    post_id: int,
    comment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    """
    댓글을 삭제하는 엔드포인트입니다.
    작성자만 삭제할 수 있으며, 소프트 삭제로 처리됩니다.
    """
    try:
        # 댓글 조회
        comment = db.exec(
            select(Comment).where(
                Comment.id == comment_id,
                Comment.post_id == post_id,
                Comment.is_deleted == False,
            )
        ).first()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="댓글을 찾을 수 없습니다."
            )

        # 작성자 확인
        if comment.user_uuid != current_user.uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="댓글을 삭제할 권한이 없습니다.",
            )

        # 소프트 삭제 처리
        comment.soft_delete()

        db.add(comment)
        db.commit()

    except HTTPException as e:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 삭제 중 오류가 발생했습니다.",
        )

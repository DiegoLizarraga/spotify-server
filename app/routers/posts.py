from typing import List
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.models.comment import Comment
from app.models.like import Like
from app.models.post import Post
from app.models.image import Image
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead
from app.schemas.like import LikeCreate, LikeRead
from app.schemas.post import PostCreate, PostRead, PostReadDetails
from app.services.cloudinary_service import cloudinary_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostRead])
async def get_posts(session: AsyncSession = Depends(get_session)):
    posts = (await session.exec(select(Post))).all()

    response = []
    for post in posts:
        images = (await session.exec(select(Image).where(Image.post_id == post.id))).all()
        likes_count = len((await session.exec(select(Like).where(Like.post_id == post.id))).all())
        comments_count = len((await session.exec(select(Comment).where(Comment.post_id == post.id))).all())
        response.append(PostRead(
            id=post.id,
            user_id=post.user_id,
            description=post.description,
            created_at=post.created_at,
            images=images,
            likes_count=likes_count,
            comments_count=comments_count,
        ))

    return response


@router.post("/", response_model=PostRead, status_code=201)
async def create_post(
    user_id: str = Form(...),
    description: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    session: AsyncSession = Depends(get_session),
):
    post = Post(description=description, user_id=uuid.UUID(user_id))
    session.add(post)
    await session.commit()
    await session.refresh(post)

    images = []
    if files and files[0].filename:
        for file in files:
            cloud_res = await cloudinary_service.upload_image(
                file,
                folder=f"postify/posts/{post.id}"
            )
            image = Image(
                url=cloud_res["url"],
                public_id=cloud_res["public_id"],
                post_id=post.id
            )
            session.add(image)
            images.append(image)
        await session.commit()

    return PostRead(
        id=post.id,
        user_id=post.user_id,
        description=post.description,
        created_at=post.created_at,
        images=images,
        likes_count=0,
        comments_count=0,
    )


@router.get("/{post_id}", response_model=PostReadDetails)
async def get_post_by_id(post_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    post = await session.get(Post, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    likes = (await session.exec(select(Like).where(Like.post_id == post_id))).all()
    raw_comments = (await session.exec(select(Comment).where(Comment.post_id == post_id))).all()
    images = (await session.exec(select(Image).where(Image.post_id == post_id))).all()

    comments = []
    for c in raw_comments:
        user = await session.get(User, c.user_id)
        comments.append(CommentRead(
            id=c.id,
            content=c.content,
            user_id=c.user_id,
            post_id=c.post_id,
            created_at=c.created_at,
            username=user.username if user else "",
        ))

    return PostReadDetails(
        id=post.id,
        user_id=post.user_id,
        description=post.description,
        created_at=post.created_at,
        images=images,
        likes=likes,
        comments=comments,
    )


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    images = (await session.exec(select(Image).where(Image.post_id == post_id))).all()
    for image in images:
        cloudinary_service.delete_image(image.public_id)
        await session.delete(image)

    likes = (await session.exec(select(Like).where(Like.post_id == post_id))).all()
    for like in likes:
        await session.delete(like)

    comments = (await session.exec(select(Comment).where(Comment.post_id == post_id))).all()
    for comment in comments:
        await session.delete(comment)

    await session.commit()
    await session.delete(post)
    await session.commit()


@router.post("/{post_id}/comments", response_model=CommentRead, status_code=201)
async def add_comment(
    post_id: uuid.UUID,
    data: CommentCreate,
    session: AsyncSession = Depends(get_session),
):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = Comment(**data.model_dump())
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


@router.post("/{post_id}/likes", response_model=LikeRead, status_code=201)
async def like_post(
    post_id: uuid.UUID,
    data: LikeCreate,
    session: AsyncSession = Depends(get_session),
):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = await session.get(Like, (data.user_id, post_id))
    if existing:
        raise HTTPException(status_code=400, detail="Like already exists")

    like = Like(user_id=data.user_id, post_id=post_id)
    session.add(like)
    await session.commit()
    await session.refresh(like)
    return like


@router.delete("/{post_id}/likes/{user_id}", status_code=204)
async def unlike_post(
    post_id: uuid.UUID,
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    like = await session.get(Like, (user_id, post_id))
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    await session.delete(like)
    await session.commit()

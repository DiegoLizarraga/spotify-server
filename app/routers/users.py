from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.models.user import User
from app.models.post import Post
from app.schemas.user import UserCreate, UserRead
from app.schemas.post import PostRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserRead])
async def get_users(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(User))
    return result.all()


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    user = User(**data.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(user)
    await session.commit()


@router.get('/{user_id}/posts', response_model=List[PostRead], status_code=200)
async def get_posts_by_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await session.exec(select(Post).where(Post.user_id == user_id))
    return result.all()


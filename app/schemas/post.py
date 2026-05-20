from datetime import datetime
from typing import List
import uuid

from sqlmodel import SQLModel

from app.schemas.comment import CommentRead
from app.schemas.like import LikeRead


class PostCreate(SQLModel):
    description: str
    user_id: uuid.UUID


class PostRead(SQLModel):
    id: uuid.UUID
    description: str
    created_at: datetime


class PostDetail(SQLModel):
    id: uuid.UUID
    description: str
    created_at: datetime
    comments: List[CommentRead] = []
    likes: List[LikeRead] = []

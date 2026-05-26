from datetime import datetime
from typing import TYPE_CHECKING, List
import uuid

from sqlmodel import SQLModel

if TYPE_CHECKING:
    from app.schemas.like import LikeRead
    from app.schemas.comment import CommentRead
    from app.schemas.image import ImageRead


class PostCreate(SQLModel):
    description: str
    user_id: uuid.UUID


class PostRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    description: str
    created_at: datetime
    images: List["ImageRead"] = []
    likes_count: int = 0
    comments_count: int = 0


class PostReadDetails(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    description: str
    created_at: datetime
    images: List["ImageRead"] = []
    likes: List["LikeRead"] = []
    comments: List["CommentRead"] = []


from app.schemas.like import LikeRead
from app.schemas.comment import CommentRead
from app.schemas.image import ImageRead

PostRead.model_rebuild()
PostReadDetails.model_rebuild()

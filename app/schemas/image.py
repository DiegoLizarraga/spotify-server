import uuid

from sqlmodel import SQLModel


class ImageCreate(SQLModel):
    url: str
    public_id: str
    post_id: uuid.UUID


class ImageRead(SQLModel):
    id: uuid.UUID
    url: str
    public_id: str
    post_id: uuid.UUID

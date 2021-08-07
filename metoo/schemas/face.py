from typing import Optional

from pydantic import BaseModel


# Shared properties
class FaceBase(BaseModel):
    group: Optional[str]
    person_id: Optional[int]
    person_name: str
    face_image: str
    face_encoding: str


# Properties to receive on face creation
class FaceCreate(FaceBase):
    group: str
    person_id: int


# Properties to receive on face update
class FaceUpdate(FaceBase):
    pass


# Properties shared by models stored in DB
class FaceInDBBase(FaceBase):
    id: int
    group: str
    person_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Face(FaceInDBBase):
    pass


# Properties properties stored in DB
class FaceInDB(FaceInDBBase):
    pass

from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.face import Face
from schemas.face import FaceCreate, FaceUpdate


class CRUDFace(CRUDBase[Face, FaceCreate, FaceUpdate]):
    def get_by_person_id(
            self, db: Session, *, group: str, person_id: int
    ) -> Face:
        return db.query(self.model).filter(Face.group == group, Face.person_id == person_id).first()

    def get_all_by_group(
            self, db: Session, *, group: str
    ) -> List[Face]:
        return (
            db.query(self.model)
                .filter(Face.group == group)
                .all()
        )


face = CRUDFace(Face)

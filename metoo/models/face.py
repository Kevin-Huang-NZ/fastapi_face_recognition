from sqlalchemy import Column, BigInteger, String, Index

from db.base_class import Base


class Face(Base):
    id = Column(BigInteger, primary_key=True)
    group = Column(String(100))
    person_id = Column(String(100))
    person_name = Column(String(100))
    face_image = Column(String(200))
    face_encoding = Column(String(4096))
    Index("idx_face_group_person_id", group, person_id, unique=True)

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, BigInteger, String
from sqlalchemy.orm import relationship

from db.base_class import Base


class Item(Base):
    id = Column(BigInteger, primary_key=True)
    title = Column(String(200), index=True)
    description = Column(String(1500), index=False)

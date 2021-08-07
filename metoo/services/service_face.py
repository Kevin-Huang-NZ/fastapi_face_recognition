import pickle
from typing import List

from aioredis import Redis
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

import crud
import schemas
from models.face import Face


async def get_all_by_group(
        db: Session, redis: Redis, *, redis_key: str, group: str
) -> List[Face]:
    if await redis.exists(redis_key):
        redis_faces = await redis.lrange(redis_key, 0, -1)
        faces = []
        for one_face in redis_faces:
            faces.append(pickle.loads(one_face))
    else:
        faces = crud.face.get_all_by_group(db=db, group=group)
        for one_face in faces:
            face_data = jsonable_encoder(one_face)
            redis_face = schemas.Face(**face_data)
            # logger.info(pickle.dumps(redis_face))
            await redis.lpush(redis_key, pickle.dumps(redis_face))
    return faces


class ServiceFace:
    pass


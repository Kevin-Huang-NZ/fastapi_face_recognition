import json
import pickle
from typing import Any, List, Optional
from fastapi.encoders import jsonable_encoder

from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Request, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import crud, models, schemas
from api import deps
import logging
from utils import upload_file
import face_recognition
from core.config import settings
from models.face import Face
from services.service_face import get_all_by_group
import numpy as np

router = APIRouter()
logger = logging.getLogger("uvicorn.info")


@router.get("/{group}", response_model=List[schemas.Face], summary="使用分组获取人脸信息列表")
async def read_all_faces_by_group(
        request: Request,
        group: str,
        db: Session = Depends(deps.get_db),
        *,
        refresh: int = Query(0)
) -> Any:
    redis = request.app.state.redis
    redis_key = f"{settings.REDIS_KEY_FACE_INFO}.{group}"

    return await get_all_by_group(db, redis, redis_key=redis_key, group=group)


@router.post("/{group}", response_model=schemas.Face, summary="创建新的人脸信息")
async def create_face(
        request: Request,
        group: str,
        *,
        db: Session = Depends(deps.get_db),
        file: UploadFile = File(...),
        person_id: int = Form(...),
        person_name: str = Form(...)
) -> Any:
    """
    创建新的人脸信息
    """
    redis = request.app.state.redis
    redis_key = f"{settings.REDIS_KEY_FACE_INFO}.{group}"
    try:
        fr_image = face_recognition.load_image_file(file.file)
        face_encodings = face_recognition.face_encodings(fr_image)
        if len(face_encodings) != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上传图片不能识别出人脸信息，请上传清晰个人照片")

        face_image = upload_file.save_upload_file(file, sub_folder=group)
        face_in = schemas.FaceCreate(
            group=group,
            person_id=person_id,
            person_name=person_name,
            face_image=face_image,
            face_encoding=json.dumps(face_encodings[0].tolist())
        )
        face = crud.face.create(db=db, obj_in=face_in)
        if await redis.exists(redis_key):
            face_data = jsonable_encoder(face)
            redis_face = schemas.Face(**face_data)
            # logger.info(pickle.dumps(redis_face))
            await redis.lpush(redis_key, pickle.dumps(redis_face))
    except IOError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="上传文件异常，请稍后再试")
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="数据已存在")
    else:
        return face


@router.put("/{group}/{person_id}", response_model=schemas.Face, summary="更新人脸信息")
async def update_face(
        request: Request,
        group: str,
        person_id: int,
        *,
        db: Session = Depends(deps.get_db),
        file: UploadFile = File(...),
        person_name: str = Form(...)
) -> Any:
    """
    更新人脸信息
    """
    redis = request.app.state.redis
    redis_key = f"{settings.REDIS_KEY_FACE_INFO}.{group}"
    try:
        face = crud.face.get_by_person_id(db=db, group=group, person_id=person_id)
        if not face:
            raise HTTPException(status_code=404, detail="人脸信息不存在")

        fr_image = face_recognition.load_image_file(file.file)
        face_encodings = face_recognition.face_encodings(fr_image)
        if len(face_encodings) != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上传图片不能识别出人脸信息，请上传清晰个人照片")

        face_image = upload_file.save_upload_file(file, sub_folder=group)
        face_in = schemas.FaceUpdate(
            person_name=person_name,
            face_image=face_image,
            face_encoding=json.dumps(face_encodings[0].tolist())
        )

        if await redis.exists(redis_key):
            face_data = jsonable_encoder(face)
            redis_face = schemas.Face(**face_data)
            # logger.info(pickle.dumps(redis_face))
            await redis.lrem(redis_key, count=0, value=pickle.dumps(redis_face))

        face = crud.face.update(db=db, db_obj=face, obj_in=face_in)

        if await redis.exists(redis_key):
            face_data = jsonable_encoder(face)
            redis_face = schemas.Face(**face_data)
            # logger.info(pickle.dumps(redis_face))
            await redis.lpush(redis_key, pickle.dumps(redis_face))
    except IOError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="上传文件异常，请稍后再试")
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="数据已存在")
    else:
        return face


@router.get("/{group}/{person_id}", response_model=schemas.Face, summary="使用分组和人的id获取一个人脸信息")
def read_face(
        group: str,
        person_id: int,
        db: Session = Depends(deps.get_db)
) -> Any:
    """
    使用分组和人的id获取一个人脸信息
    """
    face = crud.face.get_by_person_id(db=db, group=group, person_id=person_id)
    if not face:
        raise HTTPException(status_code=404, detail="人脸信息不存在")
    return face


@router.delete("/{id}", response_model=schemas.Face, summary="使用id删除一个人脸信息")
async def delete_face(
        request: Request,
        *,
        db: Session = Depends(deps.get_db),
        id: int
) -> Any:
    """
    使用id删除一个人脸信息
    """
    redis = request.app.state.redis
    face = crud.face.get(db=db, id=id)
    redis_key = f"{settings.REDIS_KEY_FACE_INFO}.{face.group}"

    if not face:
        raise HTTPException(status_code=404, detail="人脸信息不存在")

    if await redis.exists(redis_key):
        face_data = jsonable_encoder(face)
        redis_face = schemas.Face(**face_data)
        # logger.info(pickle.dumps(redis_face))
        await redis.lrem(redis_key, count=1, value=pickle.dumps(redis_face))

    face = crud.face.remove(db=db, id=id)
    return face


@router.post("/{group}/who", summary="识别人脸")
async def who(
        request: Request,
        group: str,
        *,
        db: Session = Depends(deps.get_db),
        file: UploadFile = File(...)
) -> Any:
    """
    识别人脸
    """
    redis = request.app.state.redis
    redis_key = f"{settings.REDIS_KEY_FACE_INFO}.{group}"
    include_keys = {
        "group": ...,
        "person_id": ...,
        "person_name": ...
    }
    exclude_keys = {
        "id": ...,
        "face_encoding": ...,
        "face_image": ...
    }
    persons = []
    try:
        fr_image = face_recognition.load_image_file(file.file)
        face_encodings = face_recognition.face_encodings(fr_image)
        if len(face_encodings) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上传图片不能识别出人脸信息")

        faces = await get_all_by_group(db, redis, redis_key=redis_key, group=group)
        known_face_encodings = []
        for face in faces:
            known_face_encodings.append(np.asarray(json.loads(face.face_encoding)))

        for face_encoding in face_encodings:
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            person = faces[best_match_index]
            if person:
                # persons.append(jsonable_encoder(faces[best_match_index], exclude=exclude_keys))
                persons.append({"group": person.group, "person_id": person.person_id, "person_name": person.person_name})
    except IOError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="上传文件异常，请稍后再试")
    else:
        return persons

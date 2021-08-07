from typing import Any, List

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from api import deps
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn.info")


@router.get("/", response_model=List[schemas.Item], summary="获取Item列表")
def read_items(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100
) -> Any:
    items = crud.item.get_multi(db, skip=skip, limit=limit)
    for item in items:
        logger.info("id:{},title:{},description:{}".format(type(item.id), type(item.title), type(item.description)))
    return items


@router.post("/", response_model=schemas.Item, summary="创建新的Item")
def create_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: schemas.ItemCreate
) -> Any:
    """
    Create new item.
    """
    # logger.info(item_in)
    item = crud.item.create(db=db, obj_in=item_in)
    logger.info(item)
    return item


@router.put("/{id}", response_model=schemas.Item, summary="更新Item")
def update_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    item_in: schemas.ItemUpdate
) -> Any:
    """
    更新Item
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item = crud.item.update(db=db, db_obj=item, obj_in=item_in)
    return item


@router.get("/{id}", response_model=schemas.Item, summary="使用id获取一个Item")
def read_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    """
    使用id获取一个Item
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item不存在")
    return item


@router.delete("/{id}", response_model=schemas.Item, summary="使用id删除一个Item")
def delete_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    """
    使用id删除一个Item
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item不存在")
    item = crud.item.remove(db=db, id=id)
    return item
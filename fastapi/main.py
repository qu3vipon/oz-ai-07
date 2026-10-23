from fastapi import FastAPI, Path, Query, Body, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from connection import SessionFactory
from model import Item


app = FastAPI(
    title="e-Commerce 상품 관리 서버"
)

ITEMS: list[dict[str, int | str]] = []

class ItemResponse(BaseModel):
    id: int
    name: str
    price: int

@app.get(
    "/items",
    summary="전체 상품 조회 API",
    response_model=list[ItemResponse]
)
def get_items_handler():
    session = SessionFactory()

    stmt = select(Item)
    result = session.execute(stmt)
    items: list[Item] = result.scalars().all()
    return items

@app.get(
    "/items/search",
    summary="상품 검색 API",
    response_model=list[ItemResponse]
)
def search_items_handler(
    q: str = Query(..., min_length=2)
):
    session = SessionFactory()

    stmt = select(Item).where(Item.name.contains(q))
    result = session.execute(stmt)
    items = result.scalars().all()
    if not items:
        raise HTTPException(
            status_code=404,
            detail="검색 결과가 없습니다."
        )
    return items

@app.get(
    "/items/{item_id}",
    summary="단일 상품 조회 API (상세보기)",
    response_model=ItemResponse,
)
def get_item_detail_handler(
    item_id: int = Path(..., ge=1)
):  
    session = SessionFactory()

    stmt = select(Item).where(Item.id == item_id)
    result = session.execute(stmt)
    item = result.scalar()
    if not item:
        raise HTTPException(
            status_code=404, detail="상품을 찾을 수 없습니다."
        )
    return item

class CreateItemRequest(BaseModel):
    name: str = Field(..., examples=["melon"])
    price: int = Field(..., examples=[100])

@app.post(
    "/items",
    summary="새로운 상품 등록 API",
    response_model=ItemResponse,
    status_code=201
)
def create_new_item_handler(body: CreateItemRequest): 
    session = SessionFactory()
    
    new_item = Item(name=body.name, price=body.price)
    session.add(new_item)
    session.commit()  # DB 저장
    return new_item


class UpdateItemRequest(BaseModel):
    name: str | None = None
    price: int | None = None

@app.patch(
    "/items/{item_id}",
    summary="상품 수정 API",
    response_model=ItemResponse,
)
def update_item_handler(
    item_id: int = Path(..., ge=1),
    body: UpdateItemRequest = Body(...),
):
    session = SessionFactory()

    # 조회
    stmt = select(Item).where(Item.id == item_id)
    result = session.execute(stmt)
    item = result.scalar()
    if not item:
        raise HTTPException(
            status_code=404,
            detail="상품을 찾을 수 없습니다."
        )

    # 수정
    if body.name:
        item.name = body.name
    if body.price:
        item.price = body.price

    session.commit()
    return item

@app.delete(
    "/items/{item_id}",
    summary="상품 삭제 API",
    response_model=None,
    status_code=204
)
def delete_item_handler(
    item_id: int = Path(..., ge=1),
):
    session = SessionFactory()

    stmt = select(Item).where(Item.id == item_id)
    result = session.execute(stmt)
    item = result.scalar()
    if not item:
        raise HTTPException(
            status_code=404,
            detail="상품을 찾을 수 없습니다."
        )

    session.delete(item)
    session.commit()

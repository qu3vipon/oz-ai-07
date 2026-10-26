from fastapi import FastAPI, Path, Query, Body, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select

from connection import SessionFactory, get_session
from model import Item

import anyio
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_):
    # 서버 시작 직후에 실행할 코드
    # 예: AI 모델 로드
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens == 200   # 쓰레드 풀 개수를 200개로 상향

    yield
    # 서버 종료 직전에 실행할 코드

app = FastAPI(
    title="e-Commerce 상품 관리 서버",
    lifespan=lifespan
)

class ItemResponse(BaseModel):
    id: int
    name: str
    price: int

@app.get(
    "/items",
    summary="전체 상품 조회 API",
    response_model=list[ItemResponse]
)
def get_items_handler(
    session = Depends(get_session)
):
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
    q: str = Query(..., min_length=2),
    session = Depends(get_session)
):
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
    item_id: int = Path(..., ge=1),
    session = Depends(get_session)
):  
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
def create_new_item_handler(
    body: CreateItemRequest,
    session = Depends(get_session)
): 
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
    session = Depends(get_session)
):
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
    session = Depends(get_session)
):
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

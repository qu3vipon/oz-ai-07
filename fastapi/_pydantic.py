from pydantic import BaseModel


# 내가 원하는 데이터를 표현 -> 속성 값들의 타입을 보장
class Item(BaseModel):
    id: int
    name: str
    price: int

class ItemOrigin:
    def __init__(self, id: int, name: str, price: int):
        self.id = id
        self.name = name
        self.price = price

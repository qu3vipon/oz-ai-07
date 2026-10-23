# Type Hints(타입 힌트)

# 변수 타입힌트
name: str = "alex"
price: int = 100
ratio: float = 0.3
is_active: bool = True

score: int | float = 90

# 함수 타입힌트
def add(n1: int, n2: int) -> int:
    return n1 + n2

# 컬렉션 타입(Collection Type)
names: list[str] = ["alex", "bob", "chris"]
numbers: list[int | float | None] = [100, 90.5, 80, None]

scores: dict[str, int | None] = {
    "math": 90, "eng": 100, "history": None
}


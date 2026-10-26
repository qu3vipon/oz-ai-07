# 코루틴 함수(= 비동기 함수)
async def hello():
    print("hello")

# 일반 함수: 함수 호출() -> 함수 실행

# 코루틴 함수: 함수 호출() -> 코루틴 객체 반환 -> asyncio.run(객체)
coro = hello()

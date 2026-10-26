import asyncio
import time

async def task_a():
    print("A 시작")
    time.sleep(2)
    print("A 끝")

async def task_b():
    print("B 시작")
    await asyncio.sleep(2)
    print("B 끝")

async def main():
    a = task_a()
    b = task_b()
    await asyncio.gather(a, b)

import time

start = time.time()
asyncio.run(main())
end = time.time()

print("=========================")
print(f"실행 시간: {end - start:.2f}")

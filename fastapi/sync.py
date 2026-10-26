import time

def task_a():
    print("A 시작")
    time.sleep(2)
    print("A 끝")

def task_b():
    print("B 시작")
    time.sleep(2)
    print("B 끝")

start = time.time()
task_a()
task_b()
end = time.time()

print("=========================")
print(f"실행 시간: {end - start:.2f}")

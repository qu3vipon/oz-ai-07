FROM python:3.13
WORKDIR /app
COPY . .
RUN pip install llama-cpp-python redis

# 컨테이너 실행(Run)할 때, 사용되는 명령어
CMD ["python", "-u", "main.py"]

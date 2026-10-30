# Linux + Python3.13
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install "fastapi[standard]" sqlalchemy pymysql cryptography

# 컨테이너 실행(docker run)에 사용할 명령어
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

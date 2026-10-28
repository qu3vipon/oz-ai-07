from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Body, Depends
from fastapi.responses import StreamingResponse
from llama_cpp import Llama
from openai import OpenAI

from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 직후에 실행할 코드
    app.state.llm = Llama(
        model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        n_ctx=4096,
        n_threads=2,
        verbose=False,
        chat_format="llama-3"
    )

    app.state.openai_client = OpenAI(api_key=settings.openai_api_key)
    yield
    # 서버 종료 직전에 실행할 코드

app = FastAPI(
    title="LLM 서빙 API",
    lifespan=lifespan
)

SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)

def get_llm(request: Request):
    return request.app.state.llm

@app.post("/generate")
def generate_answer_handler(
    user_input: str = Body(..., embed=True),
    llm = Depends(get_llm)
):
    def token_generator():
        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            max_tokens=512,
            temperature=0.7,
            stream=True
        )
        for chunk in response:
            token = chunk["choices"][0]["delta"].get("content")
            if token:
                yield token
    
    return StreamingResponse(
        token_generator(),  # 토큰 생성 제너레이터
        media_type="text/event-stream"  # HTTP 스트리밍 응답
    )

def get_openai_client(request: Request):
    return request.app.state.openai_client

@app.post(
    "/openai",
    summary="OpenAI API 호출"
)
def call_openai_handler(
    openai_client = Depends(get_openai_client),
    user_input: str = Body(..., embed=True)
):
    # OpenAI 서버로 HTTP 요청
    response = openai_client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": "한 줄로 짧게 답변해라"},
            {"role": "user", "content": user_input},
        ]
    )
    return {
        "answer": response.output_text
    }

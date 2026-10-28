from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Body, Depends
from llama_cpp import Llama


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 직후에 실행할 코드
    print("=== Llama 모델 로딩 시작 ===")
    app.state.llm = Llama(
        model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        n_ctx=4096,
        n_threads=2,
        verbose=False,
        chat_format="llama-3"
    )
    print("=== Llama 모델 로딩 완료 ===")
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
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        max_tokens=512,
        temperature=0.7
    )
    answer = response["choices"][0]["message"]
    return {
        "answer": answer["content"]
    }

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Body, Depends, Path
from fastapi.responses import StreamingResponse
from llama_cpp import Llama
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from sqlalchemy import select

from config import settings
from connection import get_session
from model import ChatRoom, ChatMessage


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

    app.state.openai_client = AsyncOpenAI(
        api_key=settings.openai_api_key
    )
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

@app.post(
    "/chat-rooms",
    summary="새로운 채팅방 생성 API",
)
async def create_chat_room_handler(
    title: str = Body(..., embed=True),
    session = Depends(get_session),
):
    new_chat_room = ChatRoom(title=title)
    session.add(new_chat_room)
    await session.flush()  # 커밋되지 않은 상태

    # 채팅방을 만들자마자, 시스템 프롬프트를 함께 생성
    system_prompt = ChatMessage(
        chat_room_id=new_chat_room.id,
        role="system",
        content=SYSTEM_PROMPT,
    )
    session.add(system_prompt)
    await session.commit()

    return new_chat_room

def get_llm(request: Request):
    return request.app.state.llm

# POST /chat-rooms/1/messages
@app.post(
    "/chat-rooms/{chat_room_id}/messages",
    summary="새로운 채팅 생성 API",
)
async def create_chat_message_handler(
    chat_room_id: int = Path(..., ge=1),
    user_input: str = Body(..., embed=True),
    llm = Depends(get_llm),
    session = Depends(get_session),
):
    # 사용자의 질문을 DB에 저장
    new_message = ChatMessage(
        chat_room_id=chat_room_id,
        role="user",
        content=user_input
    )
    session.add(new_message)
    await session.flush()

    # 현재 채팅방에서 이전에 나눴던 모든 메시지를 조회
    stmt = select(
        ChatMessage.role, ChatMessage.content
    ).where(
        ChatMessage.chat_room_id == chat_room_id
    ).order_by(ChatMessage.id)  # id 오름차순

    result = await session.execute(stmt)
    context = result.mappings().all()

    # 응답 생성(추론)
    response = llm.create_chat_completion(
        messages=context,
        max_tokens=512,
        temperature=0.7,
    )
    assistant_message = response["choices"][0]["message"]

    # 어시스턴스 메시지를 저장
    new_answer = ChatMessage(
        chat_room_id=chat_room_id,
        role="assistant",
        content=assistant_message["content"]
    )
    session.add(new_answer)
    await session.commit()

    return new_answer

@app.get(
    "/chat-rooms/{chat_room_id}/messages",
    summary="채팅방에서 나눈 전체 채팅 조회"
)
async def get_chat_room_messages(
    chat_room_id: int = Path(..., ge=1),
    session = Depends(get_session),
):
    stmt = (
        select(ChatMessage)
        .where(
            ChatMessage.role != "system",
            ChatMessage.chat_room_id==chat_room_id
        )
        .order_by(ChatMessage.id)
    )
    result = await session.execute(stmt)
    messages = result.scalars().all()
    return messages




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

class OpenAIResponseFormat(BaseModel):
    result: str = Field(description="답변")
    confidence: float = Field(description="0~1 사이의 답변 신뢰도")
    keywords: list[str] = Field(description="질문의 주요 키워드 3개")

@app.post(
    "/openai",
    summary="OpenAI API 호출"
)
async def call_openai_handler(
    openai_client = Depends(get_openai_client),
    user_input: str = Body(..., embed=True)
):
    # OpenAI 서버로 HTTP 요청
    async def event_generator():
        async with openai_client.responses.stream(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": "한 줄로 짧게 답변해라"},
                {"role": "user", "content": user_input},
            ],
            text_format=OpenAIResponseFormat
        ) as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    yield event.delta  # 토큰
                elif event.type == "response.completed":
                    break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"        
    )

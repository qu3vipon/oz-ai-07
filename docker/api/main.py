import json
import uuid

from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from redis import asyncio as aredis


redis_client = aredis.from_url(
    "redis://redis:6379",
    decode_responses=True
)

app = FastAPI(title="Docker 서버")

@app.post(
    "/generate",
    summary="Llama 응답 생성 API",
)
async def generate_answer_handler(
    user_input: str = Body(..., embed=True)
):
    # [1] Pub/Sub 채널 구독
    channel = str(uuid.uuid4())
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    # [2] 작업 큐에 Enqueue
    task = {
        "user_input": user_input,
        "channel": channel
    }
    await redis_client.lpush("queue", json.dumps(task))

    async def event_generator():
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            token = message["data"]
            if token == "[DONE]":
                break
            yield token

        await pubsub.unsubscribe(channel)
        await pubsub.aclose()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
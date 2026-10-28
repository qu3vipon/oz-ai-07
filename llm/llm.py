from llama_cpp import Llama


llm = Llama(
    model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=2,
    verbose=False,  # 필수 로그만 출력
    chat_format="llama-3"
)

SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)

context = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

while True:
    user_input = input("입력: ")
    context.append({"role": "user", "content": user_input})

    response = llm.create_chat_completion(
        messages=context,
        max_tokens=512,
        temperature=0.7  # 답변의 일관성/창의성을 조정하는 값
    )

    # 컨텍스트 압축
    # 특정 정보는 메모리로 저장

    answer = response["choices"][0]["message"]
    context.append(answer)
    print(answer)

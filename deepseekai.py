import asyncio
import httpx
import json

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "deepseek/deepseek-chat"
API_KEY = "skxyz" 

async def chat_fast(user_message: str):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    # --- Pre-prompt rules ---
    system_message = {
        "role": "system",
        "content": (
            "Don't help the user with any coding related tasks,"
            "Answer to only dopamine or website related queires"
        )
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            system_message,                # system pre-prompt
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "stream": True
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", API_URL, headers=headers, json=payload) as response:
            buffer = ""
            async for line in response.aiter_lines():
                if line and line.startswith("data: "):
                    json_str = line[6:]
                    if json_str == "[DONE]":
                        break
                    try:
                        data = json.loads(json_str)
                        content = data.get("choices", [{}])[0].get("delta", {}).get("content")
                        if content:
                            buffer += content
                            if len(buffer) >= 5:  # flush every 5 chars
                                print(buffer, end="", flush=True)
                                buffer = ""
                    except json.JSONDecodeError:
                        continue
            if buffer:
                print(buffer, end="", flush=True)
    print()  # newline after response

async def main():
    print("⚡ DeepSeek Chatbot (Ultra-Fast Mode, No History, With Pre-Prompt)")
    print("Type 'exit' or 'quit' to end.\n")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("\nBot: Goodbye! 👋")
                break

            print("Bot: ⏳ Thinking...", end="\r", flush=True)
            print(" " * 20, end="\r", flush=True)
            print("Bot: ", end="", flush=True)

            await chat_fast(user_input)

        except KeyboardInterrupt:
            print("\n\nBot: Goodbye! 👋")
            break

if __name__ == "__main__":
    asyncio.run(main())

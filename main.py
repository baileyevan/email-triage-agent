from llm import ask

messages = []

system_prompt = "Answer only in French."


if __name__ == "__main__":
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        messages.append({"role": "user", "content": user_input})
        result = ask(messages, system_prompt)
        print(f"Assistant: {result['text']}")
        print(f"[tokens in: {result['inputTokens']} | out: {result['outputTokens']} | stop: {result['stopReason']}]")
        messages.append({"role": "assistant", "content": result["text"]})


        

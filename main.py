import anthropic
from dotenv import load_dotenv

load_dotenv()


def ask(messages):
    client = anthropic.Anthropic()
    model = "claude-opus-5-5"

    message = client.messages.create(
        model=model,
        max_tokens=500,
        messages=messages
    )
    
    response = {}
    
    for block in message.content:
        if block.type == "text":
            response["text"] = block.text
    
    response["inputTokens"] = message.usage.input_tokens
    response["outputTokens"] = message.usage.output_tokens

    return response




messages = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    
    messages.append({"role": "user", "content": user_input})
    result = ask(messages)
    print(f"Assistant: {result['text']}")
    print(f"[tokens in: {result['inputTokens']} | out: {result['outputTokens']}]")
    messages.append({"role": "assistant", "content": result["text"]})




        

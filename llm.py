import anthropic
from dotenv import load_dotenv
import os

load_dotenv()

client = anthropic.Anthropic()
model = os.getenv("MODEL", "claude-opus-5-5")

def ask(messages, system: str | None = None):
    
    maxTokens = 1024

    args = {
        "model": model,
        "messages": messages,
        "max_tokens": maxTokens,
    }
    
    if system is not None:
        args["system"] = system
        
    message = client.messages.create(**args)
    

    response = {"text": ""}
    
    for block in message.content:
        if block.type == "text":
            response["text"] = block.text
    
    response["inputTokens"] = message.usage.input_tokens
    response["outputTokens"] = message.usage.output_tokens
    response["stopReason"] = message.stop_reason

    return response
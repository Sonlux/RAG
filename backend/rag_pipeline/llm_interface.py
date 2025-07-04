# LLM interface logic for RAG
import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_API_URL = os.getenv("LLM_API", "https://integrate.api.nvidia.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-4-maverick-17b-128einstruct")

if not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY environment variable is not set. Please check your .env file.")

client = ChatNVIDIA(
    model=LLM_MODEL,
    api_key=NVIDIA_API_KEY,
    base_url=NVIDIA_API_URL,
    temperature=0.2,
    top_p=0.7,
    max_tokens=2048,  # Increased from 1024 to 2048
)

def call_llm(prompt):
    # Returns the full response as a string (non-streaming)
    try:
        response = client.invoke([{"role": "user", "content": prompt}])
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        return f"[LLM ERROR] {e}"

def stream_llm(prompt):
    # Streams the response chunk by chunk and returns the full answer
    full_response = ""
    try:
        # Debug output removed
        chunk_count = 0
        for chunk in client.stream([{"role": "user", "content": prompt}]):
            if hasattr(chunk, 'content') and chunk.content:
                # Remove console printing to avoid duplicating output in terminal
                # print(chunk.content, end="", flush=True)
                full_response += chunk.content
                chunk_count += 1
        if chunk_count == 0:
            # No content received case
            pass
    except Exception as e:
        print(f"[LLM STREAM ERROR] {e}")
    return full_response

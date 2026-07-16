from core.llm.manager import llm
from services.chat_service import chat_service


response = chat_service.chat("Hello")
print(response.content)

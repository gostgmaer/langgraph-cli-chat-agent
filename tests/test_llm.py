# from core.llm.manager import llm
# from services.chat_service import chat_service


# response = chat_service.chat("Hello")
# print(response.content)

import inspect
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

obj = AsyncSqliteSaver.from_conn_string("checkpoints.db")

print(type(obj))
print(hasattr(obj, "__aenter__"))
print(hasattr(obj, "__aexit__"))
# LangGraph CLI Chat Agent - Complete Implementation Guide

This document serves as a comprehensive, deep-dive architectural guide into the **LangGraph CLI Chat Agent** platform. It explains every step we have implemented, how the system works internally, how memory is managed, how tools are invoked, and the complete end-to-end execution flow.

---

## 1. Core Architecture Overview

The system is built as a highly decoupled Python application designed around LangGraph for stateful agent orchestration.

- **`app.py`**: The main async entry point. It initializes the database connection, spins up the LangGraph checkpointer, injects all dependencies via the bootstrap loader, and launches the CLI interface.
- **`core/bootstrap.py`**: The Dependency Injection (DI) layer. It sets up the `SessionManager`, `ChatService`, and explicitly enforces the `GEMINI_3_1_FLASH_LITE` LLM model by passing it to the `ChatService`.
- **`services/chat_service.py`**: The bridge between the user interface and the LangGraph engine. It retrieves the current session, constructs the graph execution configuration (specifically the `thread_id`), and yields token streams.
- **`interfaces/cli/`**: The presentation layer. Uses the `rich` library to render a beautiful terminal UI with markdown streaming, spinners, and tool call logs.

---

## 2. Memory Management: Short-Term vs. Long-Term

One of the most complex features of an AI agent is memory. Rather than manually fetching and appending chat logs from a custom database table, we rely entirely on LangGraph's native state reducers and Checkpointer.

### Short-Term Memory (In-Session Context)
Short-term memory refers to how the agent remembers the conversation *during* a single interaction.
- **State Schema (`core/graph/state.py`)**: We define a `GraphState` TypedDict.
- **The `add_messages` Reducer**: The `messages` field in `GraphState` is heavily annotated (`Annotated[list[BaseMessage], add_messages]`). When a new message is yielded by the LLM or a Tool, LangGraph **does not overwrite** the `messages` list. Instead, the `add_messages` reducer mathematically appends the new message to the existing list, building the context window organically.

### Long-Term Memory (Persistence Across Restarts)
Long-term memory ensures that if you completely close the app and restart your PC, the agent still remembers the conversation.
- **Checkpointer (`core/graph/checkpointer.py`)**: We implemented LangGraph's `AsyncSqliteSaver`. Every time the graph finishes a turn, the checkpointer takes a snapshot of the entire `GraphState` (all messages and preferences) and serializes it to `data/checkpoints.db`.
- **Thread IDs (`core/memory/session.py`)**: To know *which* memory to load, the `SessionManager` tracks a `thread_id` (a UUID for the chat session). When you restart the app, `SessionManager.get_or_create()` queries the database for the most recently active session and retrieves its ID.
- **Restoration**: When `ChatService` invokes the graph, it passes `config={"configurable": {"thread_id": session.id}}`. LangGraph automatically looks inside the SQLite database for that exact ID, deserializes the past state, and injects it into short-term memory before the LLM even runs.

---

## 3. Data Mutation Controls: Remembering User Preferences

Not all memory is a chat log. Sometimes we need to overwrite specific data fields, like updating a user's favorite color.
- **The `update_preferences` Reducer**: In `GraphState`, we added a `user_preferences` dictionary. Unlike messages (which append), we wrote a custom reducer that **merges** dictionaries. If the state says `{"name": "Kishor"}`, and the agent yields `{"color": "Red"}`, the reducer combines them into `{"name": "Kishor", "color": "Red"}`.
- **Prompt Injection**: Inside `core/graph/nodes.py`, the `chatbot_node` actively reads `user_preferences` from the state and constructs a `SystemMessage` on the fly. This ensures the AI always has the latest user context loaded into its brain before generating a response.

---

## 4. How Tools Work (Tool Calling & Execution)

The agent has access to external capabilities (Tools) like saving preferences, searching Google, or checking the weather.

1. **Tool Binding**: In `nodes.py`, we call `llm.bind_tools(tools)`. This modifies the API request to Gemini, passing along JSON schemas of every available tool so the model knows what it can do.
2. **Conditional Edges (`tools_condition`)**: In `graph.py`, we set a conditional edge after the `chatbot` node. If the LLM's response contains a `tool_calls` array, the graph routes the flow to the `tools` node. If it doesn't, the graph routes to `END`.
3. **Tool Execution**: The `ToolNode` (provided by LangGraph) executes the actual Python function for the requested tool, captures the output, wraps it in a `ToolMessage`, and routes the graph *back* to the `chatbot` node so the LLM can read the tool's result.
4. **Intercepting Tools (Custom Logic)**: For the `save_preference` tool, we implemented a custom interception inside `chatbot_node`. Instead of letting the `ToolNode` run it, the `chatbot_node` intercepts the request, grabs the `key` and `value` arguments, and directly yields a `{"user_preferences": {key: value}}` state update to mutate the user's profile.

---

## 5. The Complete End-to-End Execution Flow

When a user types a message in the CLI, here is the exact chronological sequence of events:

**Step 1: Input Capture**
- The user types a message in the terminal.
- `CLI.run()` captures the text and passes it to `ChatService.stream_chat(user_message)`.

**Step 2: Session Resumption**
- `ChatService` asks `SessionManager` for the active session. 
- `SessionManager` executes a SQL query sorting by `updated_at DESC` to fetch the most recent session from the database, grabbing the active `thread_id`.

**Step 3: Graph Invocation**
- `ChatService` calls `_graph.astream_events()`.
- It passes two arguments: The new `HumanMessage`, and the `thread_id` configuration.

**Step 4: Memory Restoration (Long-Term -> Short-Term)**
- LangGraph's `AsyncSqliteSaver` intercepts the execution. 
- It queries `checkpoints.db` for the `thread_id`.
- It fully restores the past `messages` array and the `user_preferences` dictionary into active RAM.

**Step 5: The Chatbot Node (Reasoning)**
- The `add_messages` reducer appends the user's new message to the restored history.
- The `chatbot_node` pulls `user_preferences` from the state and builds a `SystemMessage` (e.g., "User's name is Kishor").
- The complete message array (System Prompt + Full History) is sent to the Gemini API.

**Step 6: LLM Decision & Branching**
- **Scenario A (Normal Conversation)**: Gemini generates a text response. The graph evaluates `tools_condition`, realizes there are no tool calls, and routes to `END`. The text is streamed back to the CLI in real-time.
- **Scenario B (Tool Required)**: Gemini realizes it needs a tool and outputs a JSON `tool_call`. The graph evaluates `tools_condition` and routes execution to the `ToolNode`. The tool runs, returns a result, and execution loops back to **Step 5** so Gemini can read the result and formulate a final answer.

**Step 7: Checkpointing (Saving State)**
- Once the graph reaches `END`, LangGraph triggers the `AsyncSqliteSaver` one last time.
- It takes the newly updated state (containing the AI's response and any new preferences) and writes it securely to the `checkpoints.db` database, ensuring it is ready for the next interaction or an application restart.

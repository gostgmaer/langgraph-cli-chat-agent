# LangGraph CLI Chat Agent — Complete Documentation

This is the single source of truth for what this system actually does today, how its pieces fit together, and what in the repo is unused scaffolding. Everything here was verified directly against the current source — not inferred from naming or old docs.

---

## 1. What This Is

A terminal chat agent built on **LangGraph** with two operating modes sharing one conversation thread:

1. **Plain chat** — a tool-using chatbot (weather, Google search, news, remembering user preferences).
2. **Multi-agent research** (`/research <topic>`) — a 7-node sub-graph (planner → human plan review → parallel search → write → review) that produces a cited, structured research report.

Conversation state is checkpointed to SQLite, so a session survives process restarts. It runs as a CLI only — `python main.py`.

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph (`StateGraph`, `Command`/`Send` dynamic routing, `interrupt()` for human-in-the-loop, `ToolNode`/`tools_condition`) |
| LLM abstraction | LangChain core + provider packages |
| LLM providers | Google Gemini (active by default), OpenAI, Anthropic, Groq, Ollama — all via one `LLMManager` class |
| Conversation persistence | LangGraph `AsyncSqliteSaver` → `CHECKPOINT_DB_PATH` |
| Session metadata persistence | SQLAlchemy 2.0 async → `DATABASE_URL` |
| Config | `pydantic-settings` reading `.env` |
| CLI rendering | `rich` (live Markdown streaming, spinners, tables) |
| Search tool | `langchain-community` `GoogleSerperAPIWrapper` (Serper.dev) |
| News tool | `langchain-tavily` `TavilySearch` |
| Weather tool | raw `httpx` call to OpenWeatherMap |
| Package management | `uv` (`pyproject.toml`) |

Requires Python **3.14+**.

---

## 3. Running It

```bash
python main.py
```

`main.py` does, in order: `init_database()` (creates the `sessions` table if missing) → opens the `Checkpointer` (SQLite, LangGraph's schema) → `create_chat_service()` (builds `LLMManager`, `SessionManager`, the compiled graph) → **renders `graph.png` and `research_graph.png`** (mermaid diagrams of the master graph and the research sub-graph, regenerated on every startup, best-effort — a render failure prints an error but doesn't block startup) → hands off to the CLI loop.

Minimum required `.env` values (see `.env.example` for the full template): `APP_NAME`, `APP_VERSION`, `DEBUG`, `LLM_PROVIDER`, `LLM_MODEL`, one matching `*_API_KEY`, `DATABASE_URL`, `CHECKPOINT_DB_PATH`, `SESSION_DB_PATH`. Search/news/weather tools degrade to an error string (not a crash) if their API key is missing.

---

## 4. Master Graph

`core/graph/graph.py` — `GraphBuilder(llm, checkpointer).build()`. State schema `State` (`TypedDict`): `messages`, `intent`, `question`, `sub_questions`, `search_results`, `revision_count`, `draft`, `final_answer`, `user_preferences`.

```
__start__ → router → chatbot ⇄ tools → __end__
                   ↘ research_team (compiled sub-graph, embedded as one node) → __end__
```

- **`router_node`** — the only classifier. If the latest message starts with `/research `, sets `intent="research"`, hard-resets every research field (`sub_questions`, `search_results`, `draft`, `revision_count`, `final_answer`), and resolves the topic (see §6, continuation). Otherwise `intent="chat"`.
- **`chatbot`** (`core/graph/nodes.py: create_chatbot_node`) — a tool-bound LLM call with a system prompt describing its actual tools truthfully. Loops with `tools` (a `ToolNode`) until the model stops calling tools. **Filters `messages` before sending them to the model**: any message with `name == "writer_agent"` (a finished `/research` report) is excluded from the prompt it builds, though it stays in `state["messages"]` for `/history`. This exists specifically so a plain "hi" after a research run doesn't resend the entire report as context (see §9).
- **`tools`** — `get_weather`, `get_google_search`, `get_news`, `save_preference`.
- **`research_team`** — the compiled research sub-graph (§5), built fresh per `GraphBuilder.build()` call but sharing the **same** `LLMManager` instance passed into `GraphBuilder` — see §7 on why that matters.

---

## 5. Research Sub-Graph

`core/graph/research/graph.py` — `ResearchGraphBuilder(llm, checkpointer).build()`. State schema `ResearchState` (`core/graph/research/state.py`).

```
__start__ → supervisor ⇄ (planner_agent → plan_review → dispatch_search →→ search_agent (parallel, one per sub-question)) ⇄ writer_agent ⇄ reviewer_agent → __end__
```

Actual edges (dumped from the compiled graph):

```
supervisor → planner_agent | writer_agent | reviewer_agent | __end__
planner_agent → plan_review
plan_review → dispatch_search | supervisor
dispatch_search → search_agent           (fan-out via langgraph.types.Send, one per sub-question)
search_agent → supervisor
writer_agent → supervisor
reviewer_agent → supervisor | writer_agent
```

**`supervisor`** (`supervisor.py`) is the routing hub — it has no LLM call, it's pure state inspection, and every other node returns to it:
1. `final_answer` already set → `END`.
2. `revision_count > MAX_REVISIONS(2)` → finalize with whatever draft exists (budget guard).
3. No `search_results` yet → `planner_agent`.
4. Results but no `draft` → `writer_agent`.
5. `draft` present, not yet reviewed → `reviewer_agent`.
6. Reviewed at least once → **finalize**: sets `final_answer`, appends exactly one `AIMessage(name="writer_agent")` to `messages`, clears `search_results`/`sub_questions`/`draft`/`revision_count`, goes to `END`.

Both finalize points (case 2 and case 6) append that one clean message — this is deliberate (see §9).

**`planner_agent`** (`planner_agent.py`) — one LLM call (`PLLANER_PROMPT`) that turns the topic into a JSON research plan (sub-questions), then hands off to `plan_review`. **Split into two nodes on purpose**: LangGraph reruns an interrupted node from the top on resume. If the LLM call sat before the `interrupt()`, every plan approve/reject/modify would silently re-run it — burning tokens and risking the dispatched plan not matching what the user actually approved. Splitting means only the cheap `plan_review` node reruns on resume.

**`plan_review`** (`planner_agent.py`) — calls `interrupt({"type": "plan_review", "question", "sub_questions"})`, pausing the graph. `ChatService.get_pending_interrupt()` surfaces this payload to the CLI, which renders the plan and prompts *approve / reject / modify*. Resuming sends `Command(resume={"action": ...})` back in. `reject` sets a cancellation `final_answer` and routes to `supervisor` (→ `END`); `approve`/`modify` route to `dispatch_search`.

**`dispatch_search`** — pure fan-out, no LLM call. `Command(goto=[Send("search_agent", {"question": sq, "messages": []}) for sq in sub_questions])` — one parallel `search_agent` invocation per sub-question.

**`search_agent`** (`search_agent.py`, factory `create_search_agent(llm)`) — a small ReAct-style loop: bind `get_google_search`+`get_news`, call the model, execute any tool calls, feed results back, repeat. Capped at `MAX_TOOL_ROUNDS = 1` extra round (so ≤2 LLM calls per sub-question). Result goes only into `search_results` — **not** appended to `messages** (intentional, see §9).

**`writer_agent`** (`writer_agent.py`, factory `create_writer_agent(llm)`) — one streamed LLM call (`WRITER_AGENT_PROMPT` + question + all `search_results`) producing `draft`. Streamed via `llm.model.astream()` so the CLI can show it live. Not appended to `messages` either — it can still be revised.

**`reviewer_agent`** (`reviewer_agent.py`, factory `create_reviewer_agent(llm)`) — one LLM call asking for a JSON consistency verdict against the draft + findings. If inconsistent and under the revision budget, clears `draft`, appends reviewer feedback to `question`, and routes **directly** to `writer_agent` (bypassing `supervisor`) for a rewrite.

---

## 6. `/research continue` (research continuation)

`core/graph/graph.py: _resolve_research_topic`. A bare `/research continue <topic>` would otherwise be treated as a literal new topic ("continue" as the research subject) — which is what it did before this was added. Now, if the raw topic starts with `continue`, `follow up`, or `follow-up` **as a whole word** (`_matches_continue_prefix` requires a non-alnum boundary, so `"continued fractions"` is not misdetected), and the thread has a prior `final_answer` in state, it builds a synthetic topic:

```
Continue and deepen the previous research on: <prev question>

Previous findings:
<prev final_answer>

Focus the follow-up research specifically on: <text after the trigger word>
   -- or, if none given --
Identify gaps, open questions, or under-explored angles in the previous findings and research those further.
```

If there's no prior `final_answer` yet, it falls back to treating the text literally (so the very first `/research continue` in a fresh thread doesn't error, it just researches "continue" literally, same as before). Deliberately **doesn't** include `"more"` or `"keep going"` as triggers — too likely to be the start of a real, unrelated topic (`/research more efficient database indexing`).

---

## 7. LLM Manager (`core/llm/manager.py`)

`LLMManager(provider?, model_name?)` wraps whichever provider `settings.llm_provider` selects (`ChatGoogleGenerativeAI` / `ChatOpenAI` / `ChatAnthropic` / `ChatGroq` / `ChatOllama`) behind one interface (`invoke`/`ainvoke`/`stream`/`astream`/`bind_tools`). **Constructing one is not free** — `__init__` eagerly builds the real provider client and logs `"Initializing <provider> provider..."`.

There is exactly **one** `LLMManager` instance for the whole process: created once in `core/bootstrap.py: create_chat_service()`, stored on `ChatService._llm`, passed into `GraphBuilder`, which passes the same instance into `ResearchGraphBuilder`, which passes it into every research-node factory (`create_planner_agent(llm)` etc.). `render_startup_diagrams()` also reuses `chat_service._llm` rather than building a second one just to draw the research diagram. This used to be 6 separate instances (one dead module-level singleton in `manager.py`, one each in 4 research-agent modules, one in bootstrap) — now it's 1.

`llm_max_tokens` (the per-request output cap) isn't a flat config value — it's derived: `llm_tpm_limit // llm_max_requests_per_minute`, so the app can't blow a provider's tokens-per-minute limit even at its own worst-case concurrency (4 parallel `search_agent` calls + planner/writer/reviewer).

---

## 8. Streaming, Step Visibility & Token Usage

`services/chat_service.py` is the whole interface between the CLI and the graph. It never exposes plain strings — everything is a `StreamChunk(type, content)`:

- **`"step"`** — a node started running. Detected via `on_chain_start` events from `astream_events(..., subgraphs=True)`, filtered to a fixed `STEP_LABELS` map (`router`, `chatbot`, `tools`, `research_team`, `supervisor`, `planner_agent`, `plan_review`, `dispatch_search`, `search_agent`, `writer_agent`, `reviewer_agent`), deduped by `run_id`, matched on `event["name"] == node_name` (not just matching `metadata.langgraph_node`, which nested internal calls also carry — this is what stops one `search_agent` invocation announcing itself 3+ times). `search_agent`'s step also shows which sub-question it's searching.
- Two extra steps derived from what a node's returned `Command` actually decided (via `on_chain_end`, reading `.goto`/`.update` off the real `Command` object): **`reviewer_agent` → `writer_agent`** yields `"🔁 Sending draft back for revision"`; **`supervisor` → `END` with a populated `final_answer`** yields `"✅ Final answer ready"`. Without these, a reviewed/finalized answer looked identical to an in-progress draft, since both are just tokens streamed from `writer_agent`.
- **`"token"`** — actual assistant text, from `on_chat_model_stream` events, restricted to nodes `chatbot`/`writer_agent` (the only two that should ever produce user-facing text).
- **`"usage"`** — one summary per `_stream_graph()` call, accumulated across **every** `on_chat_model_end` event in that run (chatbot, planner, every parallel search call, writer, reviewer) via each provider's `usage_metadata`. Rendered as `📊 Tokens — in: X · out: Y · total: Z`. Silently omitted if the provider never populates `usage_metadata` (happens with some Ollama models).

`interfaces/cli/cli.py: _consume_stream()` is the single consumer for both a fresh send and a resume-after-interrupt: a spinner covers the gap before the first event, `"step"`/`"usage"` chunks close any open live token block and print standalone, `"token"` chunks open/extend a `rich.live.Live` Markdown block.

There's also a fallback path in `_stream_graph` (word-by-word fake streaming from `final_answer` or the last message) for the case where a run reaches `END` without ever emitting a real token-stream event — e.g. the reject-plan path, or a provider that doesn't stream.

---

## 9. Why Research Content Doesn't Bloat Later Chat Turns

This was iterated on live and is worth recording precisely, since it's non-obvious:

1. Originally, `search_agent` and `writer_agent` each appended their own output to `messages` (one `HumanMessage` per parallel sub-question, plus the draft). A single research run added ~5-6 messages. Since `chatbot_node` resends the **entire** `messages` history on every plain-chat turn, a "hi" after a research run cost 15-17K input tokens.
2. **Fix, part 1**: `search_agent`/`writer_agent` no longer touch `messages` at all — they only write to `search_results`/`draft`, which is all `reviewer_agent`/`writer_agent` actually read. `supervisor` appends exactly **one** `AIMessage(name="writer_agent")` to `messages`, only at the moment a run truly finalizes. This also fixed a `/history` display bug — those messages used to be typed `HumanMessage`, so completed research answers rendered under "👤 You:" instead of "🤖 Assistant:".
3. **Fix, part 2**: even one clean message can be a multi-thousand-token report, and it was still being resent on every later chat turn. `chatbot_node` now explicitly skips any message with `name == "writer_agent"` when building what it sends to the LLM (`core/graph/nodes.py`) — it's still in `state["messages"]` (so `/history` shows it), just excluded from ongoing chat context. `/research continue` is unaffected since it reads `final_answer` directly from state, not from `messages`.
4. **Separately**: raw search-tool output was being sent to the model largely unfiltered. `get_google_search` (`core/tools/search.py`) capped to `k=5` results and now returns only title/snippet/source per result instead of the full raw Serper response (`searchParameters`, `credits`, `position`, `relatedSearches` — none of it used) — ~3,934 → ~1,644 chars per call, measured. `get_news` (`core/tools/news.py`) strips wrapper noise (`query`, `follow_up_questions`, `images`, `response_time`, `request_id`, per-result `score`) but keeps `content`, since that's the actual useful payload — smaller reduction there.
5. `search_agent`'s `MAX_TOOL_ROUNDS` was cut from 2 to 1: each round resends the full ~600-token `SEARCH_AGENT_PROMPT`, multiplied across every parallel sub-question — up to 12 resends of that prompt in a 4-sub-question run before this change, up to 8 after.

**Net effect on a fresh session**: a plain "hi" costs ~428 input tokens (measured directly — system prompt + 4 tool schemas), whether or not the thread has a completed research report sitting in its history.

**Still true, not yet acted on**: the prompt templates themselves (`core/graph/research/prompts.py`) are verbose — `SEARCH_AGENT_PROMPT` ~598 tokens, `PLLANER_PROMPT` ~715, `WRITER_AGENT_PROMPT` ~372 — and `SEARCH_AGENT_PROMPT` in particular is resent once per search round per parallel sub-question, so it's the single biggest remaining lever if further reduction is wanted. A condensed draft (~351 tokens, same rules) was prepared but not applied — it rewords actual model instructions, which is a judgment call, not free waste removal like the above.

---

## 10. Session & Persistence

Two separate SQLite-backed stores, both keyed by the same `session.id`:

- **`sessions` table** (`core/database/models/session.py`, via SQLAlchemy) — `id`, `title`, `created_at`, `updated_at`, `is_active` (defaults `True`, never flipped `False` anywhere in the code — `delete_session` hard-deletes the row rather than deactivating it).
- **LangGraph checkpoint DB** (`AsyncSqliteSaver`, `CHECKPOINT_DB_PATH`) — the actual graph state (`messages`, `search_results`, etc.) per `thread_id = session.id`.

`SessionManager.get_or_create()` (`core/memory/session.py`): if no session is cached in-process, it queries `get_active_session()` — the most-recently-`updated_at` row with `is_active=True` — and **reuses it**. Since nothing ever updates `updated_at` after creation, this is effectively "reuse the most recently *created* session." **This means restarting the app (`python main.py`) does not start a fresh conversation** — it reconnects to the same thread, checkpoint history and all. Only `/clear` (→ `ChatService.new_session()` → `SessionManager.create_session()`) actually creates a new `thread_id`.

---

## 11. CLI (`interfaces/cli/cli.py`)

Typing `/` alone shows a numbered menu and prompts for a selection (number or name); direct typed commands work too.

| Command | Behavior |
|---|---|
| `/history` | Prints the current session's message history (`ChatService.get_history()` → `state["messages"]`). |
| `/list` | Reprints the command menu. |
| `/research <topic>` | Runs the research sub-graph. Bare `/research` (no topic) prompts for one. See §6 for `continue`/`follow up`. |
| `/clear` | Clears the terminal **and** starts a brand-new session (fresh `thread_id`) — see §10 for why this is the only way to actually reset context. |
| `exit` / `quit` / `close` | Ends the CLI loop (not slash-prefixed, checked before slash-command dispatch). |

`graph.png` / `research_graph.png` are no longer CLI commands — they render automatically at every startup (§3), not on demand.

---

## 12. Tools (`core/tools/`)

| Tool | Backing service | Notes |
|---|---|---|
| `get_weather` | OpenWeatherMap (`httpx`) | Returns a formatted string; `404` → "City not found", other errors surfaced as text, never raises into the graph. |
| `get_google_search` | Serper.dev via `GoogleSerperAPIWrapper` | `k=5`, trimmed to title/snippet/source (§9). |
| `get_news` | Tavily via `TavilySearch` | `max_results=5`, trimmed to title/content/url (§9). |
| `save_preference` | In-memory only | Chatbot calls this when the user states a preference; `chatbot_node` merges it into `state["user_preferences"]` via the `update_preferences` reducer (last-write-wins per key). Not persisted outside the graph checkpoint — it lives and dies with the session's thread. |

All four degrade to a text error (missing API key, request failure) rather than throwing, so a bad/missing key never crashes a turn.

---

## 13. Configuration Surface Area vs. What's Actually Used

`config/settings.py` defines a much larger surface than the app currently exercises — it reads like the settings for a bigger platform this was scaffolded from. **Actually load-bearing**: `app_name`/`app_version`/`debug`, all `LLM_*` (provider/model/temperature/tpm/rpm/timeout), `database_url`, `sqlite_checkpoint_db`, `search_provider`-adjacent keys (`serper_api_key`, `tavily_api_key`), `weather_api_key`/`weather_api_url`, `log_level`/`log_file`. **Defined but not read by any active code path**: embeddings, vector store (Chroma/FAISS/Qdrant/pgvector), Postgres connection fields, RAG (`upload_dir`, `chunk_size`, etc.), `cli_theme`/`cli_streaming`/`cli_show_tool_calls`/`cli_show_thinking`, LangSmith tracing, `session_ttl_hours`/`max_sessions`, `sqlite_summary_db`, `max_history_messages`/`summarize_after_n_messages`. None of this is wrong to leave in place — just don't assume setting them changes behavior today.

---

## 14. Unused Scaffolding

These exist in the repo, are never imported by any active code path (verified by grep), and shouldn't be assumed to reflect current design:

- `core/graph/router.py` — `route_after_chatbot`, a TODO stub. The real routing is `route_decision` inline in `core/graph/graph.py`.
- `core/graph/research/team_subgraph.py` — explicitly labeled "illustrative" in its own comment; also imports `search_agent`/`writer_agent` as plain functions, which no longer exist post-refactor (§7) — would fail if imported.
- `core/graph/state.py` — `AgentState` (unused), `GraphState` (only used as a type *hint* on `chatbot_node`'s parameter; the graph actually runs on `State` from `graph.py`, a structurally-compatible but different `TypedDict`). Its `update_preferences` reducer function **is** real and used.
- `core/llm/formatter.py` — `LLMResponseFormatter`, unused; every place that needs this logic reimplements it inline.
- `core/llm/models.py` — `SupportedModel` enum, a reference list of model name strings. `settings.llm_model` is a plain `str`, not typed against it — purely documentation value.
- `core/memory/history.py`, `shared/decorators.py`, `shared/exceptions.py`, `shared/helpers.py`, `utils/retries.py` — not imported anywhere.

`shared/logger.py` (Rich console + rotating file handler) **is** real and used everywhere via `from shared.logger import logger`.

---

## 15. Tests (`tests/`)

Run with `python -m pytest tests/`. 8 tests, currently passing.

- `test_research_state.py` — `add_messages`/`operator.add` reducer semantics, no app code.
- `test_research_nodes.py` — `supervisor`'s pure routing logic (no LLM calls).
- `test_research_graph.py` — a fully mocked replica graph (own stub nodes) exercising `supervisor`'s finalize path end-to-end.
- `test_research_failures.py` — **exercises the real `search_agent`/`writer_agent` factories against a live LLM and live search tools** (constructs its own `LLMManager()`). Not mocked — this is an integration test in unit-test clothing; it will fail without valid API keys/network access, and does spend a small amount of real tokens/API quota when run.

---

## 16. Known Sharp Edges

- Restarting the process resumes the last session rather than starting fresh (§10) — surprising if you expect `python main.py` to mean "new conversation."
- `SEARCH_AGENT_PROMPT`/`PLLANER_PROMPT`/`WRITER_AGENT_PROMPT` are still fairly verbose relative to how often they're resent (§9) — the largest remaining, not-yet-applied token lever.
- `reviewer_agent`'s consistency check and the max-revisions budget guard both route to the same "reviewed, finalize" outcome in `supervisor` — from the outside there's no way to tell whether a finalized answer was approved because it was actually consistent, or because the revision budget just ran out.
- A rejected research plan (`plan_review`'s `reject` path) sets a cancellation `final_answer` but never appends anything to `messages`, so `/history` won't show that the user rejected a plan — the CLI shows it in the moment (via the fallback fake-streaming path), it's just not durable.

# Part 1: The Conceptual Study Guide

### 1. Core Architecture: The "Two-Brain" System
The ADK architecture separates agent knowledge into two distinct storage mechanisms. You can think of this like a computer's architecture:

*   **Sessions (RAM / Application State):**
    *   **Purpose:** Short-term context. It holds the immediate "thread" of conversation.
    *   **Content:** Raw conversational turns (`Events`) and temporary variables (`State`).
    *   **Scope:** Isolated. Session A does not know what happened in Session B.
    *   **Lifespan:** Active only during the conversation (unless persisted to a database).
*   **Memory (Hard Drive / Database):**
    *   **Purpose:** Long-term knowledge storage.
    *   **Content:** Facts, preferences, and summaries extracted from past sessions.
    *   **Scope:** Global (per user). Session B *can* search for facts learned in Session A.
    *   **Lifespan:** Persistent. Survives application restarts and spans across different conversation threads.

### 2. Key Distinctions

| Feature | **Session (`SessionService`)** | **Memory (`MemoryService`)** |
| :--- | :--- | :--- |
| **Data Type** | Raw Events (User prompts, Model replies, Tool calls) | Consolidates Facts & Knowledge |
| **Persistence** | `InMemory` (Volatile) or `Database` (Persistent) | `InMemory` (Volatile) or `VertexAI` (Cloud Persistent) |
| **Retrieval** | Automatic (The Runner feeds history to the LLM) | Tool-based (`load_memory` or `preload_memory`) |
| **Cost** | High (Process entire history every turn) | Low (Retrieve only relevant snippets) |
| **Optimization** | **Compaction**: Summarizes old turns to save tokens | **Consolidation**: Extracts key facts to reduce noise |

### 3. Essential Terminology

*   **`Runner`**: The orchestrator. It connects the Agent, Session Service, and Memory Service together. It handles the input/output loop.
*   **`Session.Events`**: The chronological list of messages in a conversation.
*   **`Session.State`**: A key-value store (dictionary) available to tools for storing structured data (e.g., `user:name = "Sam"`) within a session.
*   **`EventsCompactionConfig`**: A configuration object that tells the Runner to summarize the conversation history automatically when it gets too long, saving context window space.
*   **`ToolContext`**: The object passed to your custom tools, allowing them to read/write to `Session.State`.
*   **`Callback`**: Functions (specifically `after_agent_callback`) used to trigger automatic actions, such as saving a finished session into long-term memory.

---

# Part 2: Essential Code Patterns

These patterns refactor the notebook code into modular, production-ready blocks.

### Pattern A: The Robust Initialization
This setup ensures your agent has persistence (via SQLite) and long-term memory capabilities.

```python
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types

# 1. Configuration
retry_config = types.HttpRetryOptions(attempts=5, exp_base=2, http_status_codes=[429, 503])
model = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)

# 2. Initialize Services
# Persist short-term chats to a local file
session_service = DatabaseSessionService(db_url="sqlite:///production_sessions.db")
# For learning, we use InMemory, but in prod, this would be VertexAiMemoryBankService
memory_service = InMemoryMemoryService()

# 3. Define the Agent
agent = LlmAgent(
    model=model,
    name="Assistant",
    instruction="You are a helpful assistant with long-term memory.",
    # We will add memory tools here later
)
```

### Pattern B: Automatic Memory Ingestion (The Callback)
Instead of manually calling `add_session_to_memory` after every chat, use a callback to automate it.

```python
async def auto_save_callback(callback_context):
    """
    Automatically saves the current session state to long-term memory 
    after the agent finishes a turn.
    """
    # Access services via the context provided by ADK
    inv_context = callback_context._invocation_context
    
    await inv_context.memory_service.add_session_to_memory(
        inv_context.session
    )
    print("  [System] Session data ingested into Long-Term Memory.")

# Usage in Agent definition:
# agent = LlmAgent(..., after_agent_callback=auto_save_callback)
```

### Pattern C: Context Compaction (Optimization)
Prevent your session history from growing infinitely and consuming all your tokens.

```python
from google.adk.apps.app import App, EventsCompactionConfig

# Define compaction rules
compaction_config = EventsCompactionConfig(
    compaction_interval=5,  # Summarize every 5 turns
    overlap_size=2          # Keep the last 2 raw messages for continuity
)

# Wrap the agent in an App to apply the config
app = App(
    name="OptimizedApp",
    root_agent=agent,
    events_compaction_config=compaction_config
)

# The Runner now takes the 'app' instead of just the 'agent'
runner = Runner(
    app=app,
    session_service=session_service,
    memory_service=memory_service
)
```

### Pattern D: Stateful Tools
How to create tools that can "remember" data within the current session (Session State).

```python
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

def set_user_preference(tool_context: ToolContext, key: str, value: str) -> Dict[str, Any]:
    """Stores a specific user preference in the session state."""
    
    # Writing to state
    tool_context.state[f"pref:{key}"] = value
    return {"status": "saved", "key": key, "value": value}

def get_user_preference(tool_context: ToolContext, key: str) -> Dict[str, Any]:
    """Retrieves a preference from session state."""
    
    # Reading from state
    val = tool_context.state.get(f"pref:{key}", "Not set")
    return {"key": key, "value": val}
```

---

# Part 3: The "Master Script"

This script simulates a complete lifecycle:
1.  **Session 1:** User tells the agent a fact. The agent saves it to state and automatically ingests it into long-term memory.
2.  **Session 2:** A completely new conversation. The agent recalls the fact from memory using `preload_memory`.
3.  **Compaction:** We simulate a long conversation to trigger the automatic summarizer.

```python
import asyncio
import os
import shutil
from typing import Dict, Any

from google.adk.agents import LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import preload_memory
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# --- 1. SETUP & CONFIGURATION ---

# Ensure we have the API Key
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("Please set GOOGLE_API_KEY environment variable.")

DB_FILE = "master_script.db"
# Cleanup previous run for a clean demo
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

retry_config = types.HttpRetryOptions(attempts=3, exp_base=2, http_status_codes=[429, 503])
model = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)

# --- 2. DEFINE CUSTOM TOOLS (SESSION STATE) ---

def set_mood(tool_context: ToolContext, mood: str) -> Dict[str, Any]:
    """Records the user's current mood in the session state."""
    tool_context.state["user_mood"] = mood
    return {"status": "Mood recorded in Session State"}

# --- 3. DEFINE CALLBACKS (AUTOMATION) ---

async def auto_save_memory(callback_context):
    """Callback: Automatically ingests session data into memory after agent turns."""
    try:
        ctx = callback_context._invocation_context
        # Ingest the current session into the memory service
        await ctx.memory_service.add_session_to_memory(ctx.session)
        print("\n⚡ [System] Auto-Saved Session to Long-Term Memory.")
    except Exception as e:
        print(f"Error saving to memory: {e}")

# --- 4. INITIALIZE SERVICES & AGENT ---

# A. Services
# Persistent Short-term memory (SQLite)
session_service = DatabaseSessionService(db_url=f"sqlite:///{DB_FILE}")
# Long-term memory (RAM for demo, but represents Vector DB)
memory_service = InMemoryMemoryService()

# B. The Agent
# We use 'preload_memory' so the agent proactively searches memory before answering.
agent = LlmAgent(
    model=model,
    name="MasterAgent",
    instruction="""
    You are an intelligent assistant. 
    1. Use 'preload_memory' results to recall facts from past conversations.
    2. Use 'set_mood' if the user explicitly states how they feel.
    """,
    tools=[preload_memory, set_mood],
    after_agent_callback=auto_save_memory
)

# C. Optimization (Context Compaction)
# Triggers summarization every 3 turns to keep context tight
compaction_config = EventsCompactionConfig(
    compaction_interval=3,
    overlap_size=1
)

app = App(
    name="MasterWorkflowApp",
    root_agent=agent,
    events_compaction_config=compaction_config
)

# D. The Runner (Orchestrator)
runner = Runner(
    app=app,
    session_service=session_service,
    memory_service=memory_service
)

# --- 5. HELPER FUNCTION TO RUN CHAT ---

async def chat(session_id: str, text: str):
    print(f"\n--- 🆔 Session: {session_id} | User: {text} ---")
    user_msg = types.Content(role="user", parts=[types.Part(text=text)])
    
    async for event in runner.run_async(
        user_id="user_123", 
        session_id=session_id, 
        new_message=user_msg
    ):
        if event.is_final_response() and event.content:
             print(f"🤖 Agent: {event.content.parts[0].text}")

# --- 6. EXECUTION WORKFLOW ---

async def main():
    print("🚀 STARTING MASTER SCRIPT WORKFLOW")

    # === SCENARIO 1: TEACHING THE AGENT (Session A) ===
    # The agent will use Session State to store mood, and Memory Service to store the pet's name.
    await chat("session_A", "Hi! I am feeling happy today. Also, my dog's name is Rex.")
    
    # Verify Session State (Short-term)
    session_a = await session_service.get_session(app.name, "user_123", "session_A")
    print(f"🔍 Session A State Inspection: {session_a.state}") 
    # Expected: {'user_mood': 'happy'}

    # === SCENARIO 2: LONG-TERM RECALL (Session B) ===
    # This is a NEW session ID. Session A history is NOT loaded directly.
    # The agent must use 'preload_memory' to find "Rex" from the MemoryService.
    print("\n--- ⏳ Switching to a brand new session (Testing Long-Term Memory) ---")
    await chat("session_B", "What is my dog's name?")
    
    # === SCENARIO 3: CONTEXT COMPACTION (Session B continued) ===
    # We will spam the chat to trigger the compaction_interval (set to 3).
    print("\n--- 📉 Generating long conversation to test Compaction ---")
    await chat("session_B", "Tell me a very short fact about space.")
    await chat("session_B", "Tell me a very short fact about oceans.")
    
    # Fetch session to check for compaction event
    session_b = await session_service.get_session(app.name, "user_123", "session_B")
    
    has_compaction = False
    for event in session_b.events:
        if event.actions and event.actions.compaction:
            has_compaction = True
            print("\n✅ COMPACTION DETECTED! The history was summarized to save tokens.")
            print(f"   Summary Content: {event.actions.compaction.get('compacted_content', {}).get('parts')[0].get('text')[:100]}...")
            break
            
    if not has_compaction:
        print("\n⚠️ No compaction event found yet. (Might need one more turn depending on config/tool calls)")

if __name__ == "__main__":
    asyncio.run(main())
```
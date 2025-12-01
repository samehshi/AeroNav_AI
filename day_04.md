# Part 1: The Conceptual Study Guide

### 1. Core Architectural Concepts

**The "Black Box" Problem**
Standard software crashes with a stack trace. AI Agents fail silently—they might hallucinate, be rude, or use the wrong tool while returning a "200 OK" status. The architecture required to manage this involves two distinct loops:
1.  **The Reactive Loop (Observability):** Real-time monitoring of the agent's "thought process." This involves intercepting the lifecycle events (User Input $\rightarrow$ Agent Thought $\rightarrow$ Tool Call $\rightarrow$ Output) to log data without altering the agent's logic.
2.  **The Proactive Loop (Evaluation):** Running the agent against a "Ground Truth" dataset. This treats the agent as a system that must satisfy specific metrics, not just text similarity, but also **Trajectory Correctness** (did it take the right path to get the answer?).

**The Plugin System**
In ADK, Observability is not hardcoded into the agent's logic. It is injected via **Plugins**.
*   *Analogy:* Think of Plugins as "middleware" in a web server. They sit between the request and the response, inspecting or modifying traffic without the core application logic needing to know they exist.

**Evaluation vs. Testing**
*   *Traditional Testing:* `assert result == 5`
*   *Agent Evaluation:* "Did the agent *decide* to use the Calculator tool? Did it extract the correct parameters? Is the final text response *semantically* similar to the approved answer?"

### 2. Key Distinctions

| Feature | **Observability** (Day 4a) | **Evaluation** (Day 4b) |
| :--- | :--- | :--- |
| **Timing** | Runtime (Live/Production) | Pre-deployment (CI/CD) |
| **Goal** | Debugging & Monitoring | Regression Testing & Quality Assurance |
| **Input** | Real User Data | Canned Evaluation Sets (`.evalset.json`) |
| **Key Metric** | Latency, Error Rates, Logs | `response_match_score`, `tool_trajectory_score` |
| **Method** | Plugins & Callbacks | `adk eval` CLI or `pytest` |

### 3. Essential Terminology

*   **`LlmAgent`**: The primary class representing the AI actor. It holds the model, instructions, and tools.
*   **`Runner` (e.g., `InMemoryRunner`)**: The engine that executes the agent. It manages the session state and—crucially—is where you register **Plugins**.
*   **`Plugin`**: A class inheriting from `BasePlugin` that groups callbacks.
*   **`Callback`**: A specific hook function (e.g., `before_model_callback`) that triggers at a precise moment in the agent's execution lifecycle.
*   **`Trace`**: A visualization of the request lifecycle, showing the parent-child relationship between Agent execution, LLM calls, and Tool usage.
*   **`Trajectory`**: The specific sequence of steps (thoughts + tool calls) the agent took. In evaluation, a "correct answer" via the "wrong trajectory" (guessing) is often considered a failure.
*   **`Evaluation Set`**: A JSON collection of test cases containing prompts, expected responses, and expected tool calls.

---

# Part 2: Essential Code Patterns

### Pattern 1: The "Observable" Runner
Do not rely on `print` statements inside your functions. Use the `LoggingPlugin` attached to the Runner. This ensures standard logging across all agents.

```python
import logging
from google.adk.runners import InMemoryRunner
from google.adk.plugins.logging_plugin import LoggingPlugin

# 1. Configure standard Python logging (ADK uses this under the hood)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 2. Initialize the Runner with the Plugin
# This automatically captures User Input, LLM Requests/Responses, and Tool outputs
runner = InMemoryRunner(
    agent=my_root_agent,  # Your LlmAgent instance
    plugins=[LoggingPlugin()] 
)

# 3. Execution
# await runner.run_debug("User query here")
```

### Pattern 2: Custom Telemetry Plugin
Use this pattern to track specific business metrics (e.g., counting how many times a paid API tool is called) or to implement safety checks before the LLM runs.

```python
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest

class MetricTrackerPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="metric_tracker")
        self.tool_usage_count = 0

    # Hook: Runs BEFORE the LLM is actually called
    async def before_model_callback(
        self, 
        *, 
        callback_context: CallbackContext, 
        llm_request: LlmRequest
    ) -> None:
        # You can inspect prompt tokens here or block restricted words
        pass

    # Hook: Runs BEFORE a tool is executed
    # Note: 'agent' and 'tool' are accessible via callback_context if needed
    async def on_tool_start(self, tool_name: str, **kwargs):
        # Hypothetical hook logic (syntax depends on specific ADK version nuances)
        if tool_name == "expensive_api":
            self.tool_usage_count += 1
            print(f"💰 Expensive API called. Total: {self.tool_usage_count}")
```

### Pattern 3: Defining Evaluation Criteria
This configuration defines "Success." You verify not just what the agent said, but *how* it behaved.

```python
# test_config.json structure represented as a Dict
eval_config = {
    "criteria": {
        # Trajectory 1.0 = The agent MUST use the tools exactly as defined in the test case.
        # If it guesses the answer without using the tool, it fails.
        "tool_trajectory_avg_score": 1.0, 
        
        # Response 0.8 = The text response must be ~80% similar to the expected string.
        # This allows for minor variations in wording.
        "response_match_score": 0.8,
    }
}
```

---

# Part 3: The Master Script

This script simulates a **Tech Support Agent**. It demonstrates:
1.  **Correct Tool Typing** (fixing the bug pattern from the notebook).
2.  **Custom Observability** (a plugin to monitor tool usage).
3.  **Standard Logging** (using ADK's built-in logging).
4.  **Simulation of an Evaluation check** (programmatically verifying the result).

```python
import asyncio
import logging
import os
from typing import List, Dict

# ADK Imports
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

# --- 1. SETUP & AUTH ---
# Ensure API Key is set (In a real scenario, this comes from secrets)
if "GOOGLE_API_KEY" not in os.environ:
    # Dummy key for syntax checking if not running in authenticated env
    os.environ["GOOGLE_API_KEY"] = "AIzaSy_DUMMY_KEY"

# Configure Retry Policy (Production Best Practice)
retry_config = types.HttpRetryOptions(
    attempts=3,
    http_status_codes=[429, 500, 503]
)

# --- 2. CUSTOM OBSERVABILITY PLUGIN ---
class SecurityAuditPlugin(BasePlugin):
    """
    A custom plugin that monitors agent behavior for security/policy compliance.
    demonstrating the 'Plugins' concept from Day 4a.
    """
    def __init__(self):
        super().__init__(name="security_audit")
        self.sensitive_tools_accessed = 0

    async def before_agent_callback(
        self, *, agent: LlmAgent, callback_context: CallbackContext
    ) -> None:
        # This runs every time an agent is invoked
        print(f"\n[🛡️ AUDIT] Agent '{agent.name}' is starting a thought process...")

# --- 3. TOOL DEFINITIONS (STRICT TYPING) ---
# NOTE: The notebook emphasized using specific types (List[str]) over generic ones (str)
# to prevent agent confusion.

def reset_user_password(user_id: str, methodology: str) -> Dict[str, str]:
    """
    Resets a user's password.
    
    Args:
        user_id: The unique ID of the user.
        methodology: The method to use ('email' or 'sms').
    """
    print(f"   --> TOOL EXECUTION: Resetting password for {user_id} via {methodology}")
    return {"status": "success", "temp_password": "ChangeMe123!"}

def check_server_status(server_ids: List[str]) -> Dict[str, str]:
    """
    Checks the status of multiple servers.
    
    Args:
        server_ids: A LIST of server names to check. (Not a comma string!)
    """
    print(f"   --> TOOL EXECUTION: Pinging servers: {server_ids}")
    return {srv: "ONLINE" for srv in server_ids}

# --- 4. AGENT ARCHITECTURE ---

# Initialize Model
model = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)

# The Agent
support_agent = LlmAgent(
    name="tech_support_bot",
    model=model,
    description="Helps with account and server issues.",
    instruction="""
    You are a helpful IT support agent.
    1. If a user needs a password reset, ask for their ID and preferred method.
    2. If a user asks about servers, use 'check_server_status'.
    3. Always be polite.
    """,
    tools=[reset_user_password, check_server_status]
)

# --- 5. THE RUNTIME ENGINE (Runner + Plugins) ---

async def main():
    # Setup Logging to file (simulating production logs)
    logging.basicConfig(level=logging.INFO)
    
    print("--- 🏗️ INITIALIZING SYSTEM ---")
    
    # We attach TWO plugins here:
    # 1. LoggingPlugin: Standard ADK logging (User In -> LLM -> Tool -> Out)
    # 2. SecurityAuditPlugin: Our custom logic
    runner = InMemoryRunner(
        agent=support_agent,
        plugins=[LoggingPlugin(), SecurityAuditPlugin()]
    )

    # --- SCENARIO: EVALUATION WORKFLOW ---
    # In Day 4b, we learned to evaluate "Trajectory".
    # Let's simulate a test case: "Check servers A and B".
    # Expected Trajectory: User Input -> Tool(check_server_status) -> Response.
    
    prompt = "Can you check if server Alpha and server Bravo are running?"
    
    print(f"\n--- 🏁 RUNNING SESSION: '{prompt}' ---")
    
    # Run the agent (Observed by plugins)
    try:
        response = await runner.run_debug(prompt)
        
        print("\n--- 📊 MINI-EVALUATION (Post-Run Analysis) ---")
        # In a real 'adk eval', this logic is handled by the CLI comparing against JSON.
        # Here, we inspect the result manually to demonstrate the concept.
        
        final_text = response.get_final_response()
        print(f"Final Response: {final_text}")
        
        # Validation Logic (The "Proactive" Evaluation)
        if "ONLINE" in str(final_text) or "running" in str(final_text):
            print("✅ TEST PASSED: Response contains status info.")
        else:
            print("❌ TEST FAILED: Response missing status info.")
            
    except Exception as e:
        print(f"❌ RUNTIME ERROR: {e}")
        print("(Check logs for 'Trace' details to debug)")

# --- ENTRY POINT ---
if __name__ == "__main__":
    # In Jupyter, you would use await main()
    # In standard Python script:
    asyncio.run(main())
```
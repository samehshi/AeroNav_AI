# Part 1: The Conceptual Study Guide

### 1. Core Architecture
*   **The Bridge (Tools):** By default, an LLM is isolated. Tools are the "bridge" connecting the frozen model to dynamic data (APIs) or internal business logic (Python functions). The ADK manages the serialization of these function signatures into schemas the LLM understands.
*   **The Orchestrator (Runner/App):**
    *   **Level 1 (Basic):** `LlmAgent`. A simple wrapper around the model and tools. Good for single-turn or simple multi-turn conversations where memory is ephemeral.
    *   **Level 2 (Resumable):** `App` + `Runner`. This is required for complex workflows. It introduces a **Session Layer** (Memory) and a **State Machine**. It allows an agent to "sleep" (serialize its state to storage) while waiting for an external event (like a human approval) and "wake up" (resume) exactly where it left off.
*   **The Universal Connector (MCP):** The **Model Context Protocol** is treated as the "USB-C for Agents." Instead of writing custom Python code to talk to GitHub, Slack, or SQL, you connect the Agent to a standardized "MCP Server." The Agent (Client) automatically discovers the server's capabilities.

### 2. Key Distinctions

| Concept | Distinction |
| :--- | :--- |
| **Function Tool** vs. **Agent Tool** | A **Function Tool** executes a specific code block (e.g., `calculate_tax`). An **Agent Tool** delegates a high-level goal to a specialist agent (e.g., `tax_expert_agent`), allowing for modular "Agent-as-a-Tool" architectures. |
| **Tools** vs. **Sub-Agents** | **Tools (Delegation):** Agent A calls Agent B, gets a result, and Agent A finishes the job. **Sub-Agents (Handoff):** Agent A transfers the user entirely to Agent B; Agent A is no longer involved. |
| **Stateless** vs. **Resumable** | **Stateless:** If the process dies, the context is lost. **Resumable:** Uses an `App` container and `SessionService`. Essential for "Human-in-the-Loop" (HITL) scenarios where the wait time could be minutes or days. |

### 3. Terminology Checklist

*   **`LlmAgent`**: The primary class defining the persona, model, and instructions.
*   **`ToolContext`**: A special object injected into tool functions by ADK. It provides methods to request confirmation (`request_confirmation`) and read state.
*   **`AgentTool`**: A wrapper that converts an `LlmAgent` into a callable tool for another agent.
*   **`McpToolset`**: The class responsible for connecting to external MCP servers (via `StdioConnectionParams`).
*   **`ResumabilityConfig`**: Configuration object passed to an `App` to enable state persistence.
*   **`adk_request_confirmation`**: The specific system event fired when a tool needs to pause for human input.
*   **`invocation_id`**: The unique ID required to **resume** a paused agent workflow.

---

# Part 2: Essential Code Patterns

### 1. The "Golden Standard" Custom Tool
*ADK tools require strict typing, clear docstrings (for the LLM), and a structured dictionary return.*

```python
from google.adk.tools import ToolContext

# 1. Type hints are mandatory for schema generation
def corporate_action_tool(resource_id: str, action: str) -> dict:
    """
    Performs a corporate action on a specific resource.
    
    Args:
        resource_id: The ID of the resource (e.g., "HR-101").
        action: The action to perform (e.g., "approve", "deny").
        
    Returns:
        A dictionary containing the 'status' and 'data' or 'error_message'.
    """
    valid_actions = ["approve", "deny"]
    
    if action not in valid_actions:
        # 2. Structured Error Handling
        return {
            "status": "error",
            "error_message": f"Invalid action. Must be one of: {valid_actions}"
        }
    
    # 3. Success Response
    return {
        "status": "success",
        "data": {"resource": resource_id, "result": "processed"}
    }
```

### 2. Long-Running Operation (HITL) Pattern
*The logic strictly follows: Check if resuming -> If not, Request Confirmation -> Return Pending.*

```python
def sensitive_operation_tool(amount: int, tool_context: ToolContext) -> dict:
    """Transfers money. Requires approval for high amounts."""
    
    # SCENARIO A: Resuming (User already approved/rejected)
    if tool_context.tool_confirmation:
        if tool_context.tool_confirmation.confirmed:
            return {"status": "success", "message": "Transfer complete."}
        else:
            return {"status": "rejected", "message": "User denied transfer."}

    # SCENARIO B: First run (Need to pause?)
    THRESHOLD = 1000
    if amount > THRESHOLD:
        # Pause execution here
        tool_context.request_confirmation(
            hint=f"Transfer of ${amount} requires approval.",
            payload={"amount": amount}
        )
        # Return pending status to Agent (Agent waits)
        return {"status": "pending", "message": "Waiting for approval..."}

    # SCENARIO C: Auto-approve small amounts
    return {"status": "success", "message": "Auto-approved small transfer."}
```

### 3. The Resumable Runtime Setup
*You cannot use `LlmAgent` directly for HITL; you must wrap it in an `App`.*

```python
from google.adk.apps.app import App, ResumabilityConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.function_tool import FunctionTool

# 1. Define Agent
agent = LlmAgent(..., tools=[FunctionTool(func=sensitive_operation_tool)])

# 2. Wrap in App with Resumability
app = App(
    name="financial_app",
    root_agent=agent,
    resumability_config=ResumabilityConfig(is_resumable=True)
)

# 3. Create Session Service (Memory) and Runner
session_service = InMemorySessionService()
runner = Runner(app=app, session_service=session_service)
```

---

# Part 3: The "Master Script"

This script simulates a **Cloud Infrastructure Manager**. It combines:
1.  **Custom Tools:** A simple budget checker.
2.  **Agent-as-a-Tool:** A mathematical specialist to calculate server costs.
3.  **Long-Running Operation:** A deployment tool that pauses for approval if the cost is high.
4.  **Workflow Logic:** Manually handling the `adk_request_confirmation` event to simulate a human clicking "Approve".

```python
import asyncio
import os
import uuid
from google.genai import types

# ADK Imports
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool, ToolContext, FunctionTool
from google.adk.apps.app import App, ResumabilityConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.code_executors import BuiltInCodeExecutor

# --- CONFIGURATION ---
try:
    # Ensure GOOGLE_API_KEY is set in your environment
    API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    print("❌ Error: GOOGLE_API_KEY environment variable not set.")
    exit(1)

retry_config = types.HttpRetryOptions(attempts=3, exp_base=2, initial_delay=1)

# --- 1. SPECIALIST AGENT (Agent-as-a-Tool) ---
# This agent specializes in math/code to calculate costs accurately.
calc_agent = LlmAgent(
    name="CostCalculator",
    model=Gemini(model="gemini-2.0-flash-lite", retry_options=retry_config),
    instruction="You are a calculator. Output ONLY the numeric result of the calculation via Python code.",
    code_executor=BuiltInCodeExecutor() 
)

# --- 2. CUSTOM TOOLS ---

def check_budget_tool(department: str) -> dict:
    """Checks the remaining budget for a department."""
    # Mock database
    budgets = {"engineering": 5000, "marketing": 1000}
    remaining = budgets.get(department.lower(), 0)
    return {"status": "success", "remaining_budget": remaining}

def deploy_infrastructure_tool(resource_type: str, count: int, estimated_cost: float, tool_context: ToolContext) -> dict:
    """
    Deploys cloud resources. 
    PAUSES for approval if estimated_cost > $500.
    """
    APPROVAL_THRESHOLD = 500.0

    # CASE A: Resuming after human input
    if tool_context.tool_confirmation:
        if tool_context.tool_confirmation.confirmed:
            return {
                "status": "success", 
                "deployment_id": f"DEP-{uuid.uuid4().hex[:6].upper()}",
                "message": "Deployment authorized and completed."
            }
        else:
            return {"status": "rejected", "message": "Deployment cancelled by user."}

    # CASE B: First run, check threshold
    if estimated_cost > APPROVAL_THRESHOLD:
        print(f"\n[SYSTEM] ⚠️ High cost detected (${estimated_cost}). Requesting approval...")
        tool_context.request_confirmation(
            hint=f"Cost ${estimated_cost} exceeds auto-approval limit.",
            payload={"cost": estimated_cost, "resource": resource_type}
        )
        return {"status": "pending", "message": "Awaiting human approval."}

    # CASE C: Auto-approve
    return {
        "status": "success", 
        "deployment_id": f"DEP-{uuid.uuid4().hex[:6].upper()}",
        "message": "Auto-deployment successful."
    }

# --- 3. ROOT AGENT & APP SETUP ---

# The main manager that uses the specialist and the functions
infra_manager = LlmAgent(
    name="InfraManager",
    model=Gemini(model="gemini-2.0-flash-lite", retry_options=retry_config),
    instruction="""
    You are an Infrastructure Manager.
    1. Always use the 'CostCalculator' tool to calculate the total cost (count * price_per_unit). 
       (Assume Server=$100/unit, DB=$200/unit).
    2. Check the department budget using 'check_budget_tool'.
    3. If budget allows, call 'deploy_infrastructure_tool'.
    4. Handle 'pending' status by telling the user you are waiting.
    5. Report final status clearly.
    """,
    tools=[
        FunctionTool(check_budget_tool),
        FunctionTool(deploy_infrastructure_tool),
        AgentTool(agent=calc_agent) # Integrating the specialist agent
    ]
)

# Wrap in Resumable App
infra_app = App(
    name="cloud_ops_app",
    root_agent=infra_manager,
    resumability_config=ResumabilityConfig(is_resumable=True)
)

session_service = InMemorySessionService()
runner = Runner(app=infra_app, session_service=session_service)

# --- 4. WORKFLOW ORCHESTRATOR (The Event Loop) ---

async def run_scenario(user_query: str, auto_approve: bool = True):
    print(f"\n{'='*50}")
    print(f"User Request: {user_query}")
    print(f"{'='*50}")

    session_id = str(uuid.uuid4())
    await session_service.create_session(app_name="cloud_ops_app", session_id=session_id)
    
    user_msg = types.Content(role="user", parts=[types.Part(text=user_query)])
    
    # Track the Invocation ID to resume later
    pause_info = None

    # --- PHASE 1: Initial Run ---
    print(">>> Agent Running...")
    async for event in runner.run_async(user_id="admin", session_id=session_id, new_message=user_msg):
        # Detect Text Response
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: print(f"🤖 Agent: {part.text}")
        
        # Detect Pause Request (The "adk_request_confirmation" event)
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call and part.function_call.name == "adk_request_confirmation":
                    pause_info = {
                        "approval_id": part.function_call.id,
                        "invocation_id": event.invocation_id # CRITICAL: Needed to resume
                    }

    # --- PHASE 2: Handle Pause (Simulate Human) ---
    if pause_info:
        print(f"\n⏸️  SYSTEM PAUSED: High Value Transaction detected.")
        print(f"👤 Human Admin Decision: {'✅ APPROVE' if auto_approve else '❌ DENY'}")
        
        # Construct the approval response payload
        confirmation_resp = types.FunctionResponse(
            id=pause_info["approval_id"],
            name="adk_request_confirmation",
            response={"confirmed": auto_approve}
        )
        resume_msg = types.Content(role="user", parts=[types.Part(function_response=confirmation_resp)])

        # --- PHASE 3: Resume Execution ---
        print(">>> Resuming Agent...\n")
        async for event in runner.run_async(
            user_id="admin", 
            session_id=session_id, 
            new_message=resume_msg,
            invocation_id=pause_info["invocation_id"] # Passing the key to unlock the frozen state
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text: print(f"🤖 Agent: {part.text}")

# --- 5. EXECUTION ---
if __name__ == "__main__":
    # Scenario: High cost deployment (> $500) triggers approval flow
    asyncio.run(run_scenario("Deploy 6 Servers for Engineering. Check if we have budget."))
```
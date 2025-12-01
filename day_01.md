# Part 1: The Conceptual Study Guide

### 1. The Core Framework
**Library:** `google-adk` (Google Agent Development Kit)
**Underlying Engine:** Google Gemini (via `google-genai`)

The ADK is a framework designed to move beyond simple "Prompt-Response" interactions into **Agentic Workflows**. It treats LLMs not just as text generators, but as reasoning engines that can use tools, maintain state, and collaborate.

### 2. Core Concepts & Analogies

*   **The Agent (The Worker):** An agent is an LLM configuration with a specific "Job Description" (Instruction), a specific "Skill Level" (Model), and a set of "Equipment" (Tools).
*   **The Runner (The Manager):** The component that actually executes the work. It initializes the session, manages the chat history, handles errors, and routes messages between the user and the agent.
    *   *Analogy:* The Agent is the employee handbook; the Runner is the project manager ensuring the employee is actually working.
*   **Multi-Agent Systems (The Department):** Instead of one "God-mode" agent doing everything (which leads to confusion and hallucinations), you split tasks among specialists.
*   **State Management ( The Clipboard):**
    *   In ADK, state is passed implicitly via **`output_key`**.
    *   If Agent A produces `output_key="research"`, Agent B can access it in their instructions simply by using the placeholder `{research}`.
    *   *Analogy:* An assembly line where one robot places a part (Output) on the conveyor belt, and the next robot grabs exactly that part (Input) to work on it.

### 3. Workflow Patterns (The Architectures)

1.  **Dynamic Orchestration (The General Manager):** A root agent has other agents listed as **Tools**. The LLM decides *if* and *when* to call them.
    *   *Pros:* Flexible. *Cons:* Unpredictable order.
2.  **Sequential (The Assembly Line):** A fixed list of agents (`[A, B, C]`). A runs, passes output to B, B passes to C.
    *   *Pros:* Deterministic, easy to debug.
3.  **Parallel (The Task Force):** Multiple agents run at the exact same time. Usually followed by an "Aggregator" agent to merge results.
    *   *Pros:* Fast (concurrency). *Cons:* Agents cannot see each other's work while running.
4.  **Loop (The Quality Control Cycle):** A set of agents run repeatedly until a specific condition (like an "APPROVED" message) breaks the loop.

### 4. Essential Terminology

*   **`Agent`**: The standard class for a single LLM unit.
*   **`SequentialAgent` / `ParallelAgent` / `LoopAgent`**: Specialized classes for defining workflow logic.
*   **`AgentTool`**: A wrapper that turns an *Agent* into a *Tool* so another Agent can call it.
*   **`FunctionTool`**: A wrapper that turns a Python function into a Tool the Agent can execute (essential for stopping loops or saving files).
*   **`output_key`**: The variable name where an agent's result is stored in the session memory.
*   **`InMemoryRunner`**: The local execution engine used for development and debugging.

---

# Part 2: Essential Code Patterns

### 1. The "State-Aware" Agent
This pattern shows how to define an agent that writes to memory (`output_key`) and an agent that reads from it (using `{key}`).

```python
from google.adk.agents import Agent

# Producer: Saves output to 'concept_draft'
concept_agent = Agent(
    name="ConceptGenerator",
    model="gemini-2.5-flash-lite",
    instruction="Generate a high-level concept for a mobile app about gardening.",
    output_key="concept_draft"  # <--- CRITICAL: Saves state here
)

# Consumer: Reads '{concept_draft}'
developer_agent = Agent(
    name="TechLead",
    model="gemini-2.5-flash-lite",
    instruction="""
    Review this concept: {concept_draft} 
    Propose a technical stack (Frontend, Backend, DB) to build it.
    """,
    # No output_key needed if this is the final step
)
```

### 2. The Parallel Aggregation Pattern
Use this when you need to research multiple independent topics fast and then summarize them.

```python
from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.tools import google_search

# 1. Define Workers
researcher_1 = Agent(name="MarketRes", tools=[google_search], output_key="market_data", ...)
researcher_2 = Agent(name="TechRes", tools=[google_search], output_key="tech_data", ...)

# 2. Bundle them in Parallel
parallel_team = ParallelAgent(
    name="ResearchTeam",
    sub_agents=[researcher_1, researcher_2]
)

# 3. Aggregator (Runs AFTER parallel team finishes)
aggregator = Agent(
    name="Summarizer",
    instruction="Combine {market_data} and {tech_data} into a report.",
    output_key="final_report"
)

# 4. Sequential Wrapper (Parallel Block -> Aggregator)
workflow = SequentialAgent(
    name="FullWorkflow",
    sub_agents=[parallel_team, aggregator]
)
```

### 3. The "Critic Loop" (Iterative Refinement)
This requires a specific Python function to break the loop.

```python
from google.adk.agents import LoopAgent
from google.adk.tools import FunctionTool

# 1. The Exit Condition
def approve_work():
    """Call this ONLY when the work is perfect."""
    return {"status": "approved", "message": "Exiting loop."}

# 2. The Worker (Writer)
writer = Agent(
    name="Writer",
    instruction="Write or rewrite the email based on feedback.",
    output_key="draft"
)

# 3. The Decider (Critic/Manager)
manager = Agent(
    name="Manager",
    instruction="""Review the {draft}. 
    If good, call `approve_work`. 
    If bad, output critique as text.""",
    tools=[FunctionTool(approve_work)] # Give tool to the decider
)

# 4. The Loop
refinement_cycle = LoopAgent(
    name="RefinementCycle",
    sub_agents=[writer, manager],
    max_iterations=3 # Safety net
)
```

---

# Part 3: The "Master Script"

This script simulates a **Product Launch Headquarters**.
1.  **Parallel:** Two analysts research Competitors and Customer Sentiment simultaneously.
2.  **Sequential:** A Strategist synthesizes this into a Strategy Document.
3.  **Loop:** A Copywriter and a Legal Compliance officer iterate on a Press Release until it is "Legally Cleared".

```python
import asyncio
import os

# Import ADK Components
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search, FunctionTool

# --- SETUP: HELPER FUNCTIONS ---

def legal_sign_off():
    """
    Call this function ONLY when the text meets all compliance requirements
    and is ready for publication. This stops the revision process.
    """
    return {"status": "approved", "message": "Legal sign-off granted. Process complete."}

# --- STEP 1: PARALLEL RESEARCH TEAM ---

# Analyst 1: Competitor Analysis
competitor_analyst = Agent(
    name="CompetitorAnalyst",
    model="gemini-2.5-flash-lite",
    instruction="""
    Research the top 2 competitors in the 'Smart Home Coffee Maker' market.
    List their key features and price points. Keep it brief.
    """,
    tools=[google_search],
    output_key="competitor_data"
)

# Analyst 2: Customer Sentiment
sentiment_analyst = Agent(
    name="SentimentAnalyst",
    model="gemini-2.5-flash-lite",
    instruction="""
    Find recent user complaints or feature requests for smart coffee makers.
    What do people hate? What do they want? Keep it brief.
    """,
    tools=[google_search],
    output_key="customer_sentiment"
)

# Group them to run simultaneously
research_phase = ParallelAgent(
    name="ResearchPhase",
    sub_agents=[competitor_analyst, sentiment_analyst]
)

# --- STEP 2: STRATEGY SYNTHESIS (SEQUENTIAL) ---

strategist = Agent(
    name="Strategist",
    model="gemini-2.5-flash-lite",
    instruction="""
    You are the Product Strategist. Read the following data:
    
    Competitor Data: {competitor_data}
    Customer Sentiment: {customer_sentiment}
    
    Create a 'Launch Strategy' bulleted list (3 points) that highlights 
    how our product solves user complaints better than competitors.
    """,
    output_key="launch_strategy"
)

# --- STEP 3: DRAFTING & COMPLIANCE LOOP ---

# The Writer creates/updates the draft
copywriter = Agent(
    name="Copywriter",
    model="gemini-2.5-flash-lite",
    instruction="""
    You are the Copywriter.
    Strategy: {launch_strategy}
    Current Draft: {press_release_draft} (If empty, write the first draft).
    Legal Feedback: {legal_feedback} (If exists, fix the issues).
    
    Write a short, punchy Press Release (approx 100 words) for the 'BrewMaster AI'.
    """,
    output_key="press_release_draft"
)

# The Compliance Officer reviews and decides to Loop or Quit
compliance_officer = Agent(
    name="ComplianceOfficer",
    model="gemini-2.5-flash-lite",
    instruction="""
    You are Legal Compliance. Review the {press_release_draft}.
    
    Rules:
    1. No false promises (e.g., "Makes you live forever").
    2. No attacking competitors by name.
    
    Decisions:
    - IF the draft violates rules: Output specific feedback instructions.
    - IF the draft is safe: You MUST call the `legal_sign_off` tool.
    """,
    output_key="legal_feedback",
    tools=[FunctionTool(legal_sign_off)] # The tool that breaks the loop
)

# The Refinement Loop
drafting_phase = LoopAgent(
    name="DraftingLoop",
    sub_agents=[copywriter, compliance_officer],
    max_iterations=4 # Allow up to 3 revisions + 1 final check
)

# --- STEP 4: THE MASTER ORCHESTRATOR ---

# Combine all phases: Parallel Research -> Strategist -> Drafting Loop
master_workflow = SequentialAgent(
    name="ProductLaunchSystem",
    sub_agents=[
        research_phase,  # Step 1
        strategist,      # Step 2
        drafting_phase   # Step 3
    ]
)

# --- EXECUTION ---

async def main():
    print("🚀 Initializing Product Launch HQ...")
    
    # We pass an empty string for press_release_draft initially so the Copywriter doesn't crash on first run
    # (Note: ADK handles missing keys gracefully usually, but this is best practice for clarity)
    
    runner = InMemoryRunner(agent=master_workflow)
    
    print("🤖 System Running... (This involves Search, Strategy, and Iterative Legal Review)")
    
    # Trigger the workflow
    response = await runner.run_debug("Start the launch preparation for 'BrewMaster AI'")
    
    # Printing the final result (The last output from the pipeline)
    print("\n✅ WORKFLOW COMPLETE")
    print("-" * 50)
    # The runner output is complex, but the last text usually contains the final system state or response
    print(response)

# Run the async main loop
if __name__ == "__main__":
    try:
        # Check for API Key
        if "GOOGLE_API_KEY" not in os.environ:
            print("❌ Error: GOOGLE_API_KEY environment variable not set.")
        else:
            asyncio.run(main())
    except Exception as e:
        print(f"Runtime Error: {e}")
```
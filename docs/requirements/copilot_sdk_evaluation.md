# Why GitHub Copilot SDK Is Not Used as the LLM Provider

## Context

The GitHub Copilot SDK (`github-copilot-sdk`) was evaluated as a potential LLM provider for generating pedagogical feedback in the AI Phonics Tutor. This document explains why it was not selected.

## Current Approach

The app uses a direct Azure OpenAI API call via the `openai` Python SDK in `apps/ai_tutor/llm_client.py`. This is a simple, synchronous request → response pattern: send a rendered prompt, receive 1–2 sentences of child-appropriate feedback.

## Reasons the Copilot SDK Is Not a Fit

### 1. Paradigm Mismatch

The Copilot SDK is an **agentic runtime** designed for multi-turn developer workflows (tool invocation, file edits, planning). It spawns a CLI subprocess, communicates via JSON-RPC, and uses async event-driven sessions. The app only needs a constrained single-turn completion — a one-sentence encouragement like *"Great try! Move your tongue forward for /sh/."*

### 2. Async-Only Architecture

The SDK is `async/await` native. The Django views in this project are synchronous. Integrating would require either converting views to `async def` or wrapping every call in `asyncio.run()`, adding complexity for no benefit.

### 3. Process Overhead

The SDK spawns and manages a Copilot CLI subprocess per client instance. For a web server handling concurrent requests, this introduces significant resource overhead compared to a stateless HTTP API call.

### 4. Loss of Safety Controls

The current design relies on precise control over `max_tokens` (100), `temperature` (0.3), and structured system prompts to enforce child-safety constraints. The Copilot SDK's session-based interface does not expose these parameters in the same way, undermining the safety architecture defined in Tasks 3.8 and 3.9.

### 5. Latency

The extra hop through a CLI subprocess + JSON-RPC adds latency versus a direct API call. The app has a strict < 1.5 second target for speech feedback, and the additional overhead works against this.

### 6. Not Production-Ready

As of April 2026, the Copilot SDK is in **public preview** and states it *"may not yet be suitable for production use."*

### 7. Authentication & Billing Complexity

The SDK requires a GitHub Copilot subscription or BYOK (Bring Your Own Key). BYOK simply routes to the same providers (Azure OpenAI, OpenAI, Anthropic) that can be called directly — adding an unnecessary intermediary layer. Billing is tied to GitHub's premium request quota, which is harder to predict and manage than direct API usage.

## Recommendation

For multi-provider flexibility, the app should instead introduce a lightweight provider abstraction in `llm_client.py` controlled by an environment variable (e.g., `LLM_PROVIDER=azure|openai|anthropic`). This gives access to the same underlying models without the overhead of an agentic runtime. The Copilot SDK is better suited for building coding agents and developer tools — not constrained pedagogical feedback in a child-safety web application.

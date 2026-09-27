✅ **Correct — C**

A **`PreToolUse` hook** is the appropriate preventive control because it runs **before** the tool executes. Exiting with **code 2** blocks the call and sends the hook's stderr back to Claude.

---

**Message Batches API status/results**

Memorize this distinction:

```text
Batch processing status:
  in_progress
  canceling
  ended

Individual result.type:
  succeeded
  errored
  canceled
  expired
```

And:

> **No webhook → poll.**
> **Results are JSONL → don't assume order.**
> **Use `custom_id` to correlate each result.**
> **Batch expires after 24 hours; results remain available for 29 days.**

# 5-Point Last-Minute Review

### 1. Messages API = stateless

Always think:

**Application owns conversation history → resend messages.**

### 2. Tool calling mechanics

Know these cold:

```text
auto   → Claude decides
any    → must call a tool
tool   → force specific tool
none   → no tools
```

Every `tool_use` requires a matching `tool_result` with the same `tool_use_id` in the **next user turn**.

### 3. Claude Code enforcement

This distinction is highly testable:

```text
CLAUDE.md       → guidance
settings.json   → permissions
PreToolUse      → prevent
PostToolUse     → react after execution
exit code 2     → block tool call
```

### 4. Prompt caching

Remember:

```text
tools → system → messages
             ↑
       stable prefix
```

`ephemeral` → **5-minute default TTL**
Optional → **1-hour TTL**
Cache reads → ~**0.1×** input cost
5-minute cache writes → ~**1.25×**

### 5. Workflow vs Agent

```text
Known deterministic path → Workflow

Sequential dependencies  → Prompt chaining

Independent tasks        → Parallelization

Choose one path          → Routing

Iterative refinement     → Evaluator-optimizer

Dynamic process/tool     → Agent
```

**One final exam strategy:** when two answers both sound reasonable, favor the one that uses the **actual Anthropic mechanism** rather than relying on model instructions alone. This distinction shows up repeatedly in Claude API, MCP, and Claude Code questions.

# CCDV-F: 10-Point Last-Minute Review

## 1. Guidance vs. Mechanism (your #1 trap)
- **Guidance:** `CLAUDE.md`, system prompts, instructions. Helpful, but **not enforced**.
- **Mechanism:** hooks, permission allow/deny rules, `--allowedTools`, code-level checks.
- Costly or adversarial failure → **mechanism**. "Should" or "occasional deviation OK" → **guidance** can be enough.
- Prefer **prevention** (`PreToolUse` exit code 2) over **detection** (`PostToolUse`, `Stop`, log review).
- Eliminate any option that satisfies one requirement by breaking another.

## 2. Extended Thinking Rules
- `tool_choice` with thinking: **only `auto` or `none`**. `any` and forced `tool` → 400.
- `budget_tokens` ≥ 1024 and **< `max_tokens`** (older `enabled` form). Newer models use `thinking: {"type": "adaptive"}` plus `effort`.
- Responses put `thinking` blocks **before** `text`. **Select blocks by type, never `content[0]`.**
- In tool loops, pass the thinking blocks back unchanged.

## 3. Tool Use Loop
- Continue while `stop_reason == "tool_use"`. Append the **full** assistant `content`.
- Every `tool_use` needs a `tool_result` with the **same `tool_use_id`** in the next user turn.
- Failures: `is_error: true` plus a descriptive, actionable message. Don't crash, and don't send an empty result.
- `any` + `disable_parallel_tool_use: true` = **exactly one** tool call.
- Tool descriptions matter most: explain what the tool does, when and when not to use it, and parameter formats.

## 4. Streaming
- Event order: `message_start` → `content_block_start` → `content_block_delta` → `content_block_stop` → **`message_delta`** → `message_stop`.
- Final `stop_reason` and cumulative `usage` arrive in **`message_delta`**.
- Tool input: `content_block_start` has `input: {}`. **Buffer `partial_json` per block index** and parse at `content_block_stop`.
- Stream when `max_tokens` is large, to avoid HTTP timeouts.

## 5. Message Batches
- Status values: `in_progress` → `canceling` → **`ended`** (never "completed").
- Results are JSONL in **no guaranteed order**. Match by **`custom_id`**.
- `result.type` is `succeeded`, `errored`, `canceled`, or `expired`. Only `succeeded` has `.message`.
- 24-hour expiry, results kept 29 days, **no webhooks** (poll), about 50% cost savings.

## 6. Prompt Caching and Files
- `cache_control: {"type": "ephemeral"}`. Default TTL is 5 minutes (refreshed on each hit); a 1-hour option exists.
- Writes cost about 1.25× base input; reads about **0.1×**.
- Prefix order: **tools → system → messages**. Anything that changes before a breakpoint (such as a timestamp) → **0 cache hits**.
- Up to 4 breakpoints, and there's a minimum cacheable length.
- The Files API avoids re-uploading files. It does **not** cache prompts automatically.

## 7. MCP
- Primitives: **Tools** = model-controlled, **Resources** = application-controlled (read-only), **Prompts** = user-controlled (slash commands).
- Transports: **stdio** for local subprocesses, **Streamable HTTP** for remote servers (SSE deprecated).
- Scope precedence: **local > project > user**.
- `.mcp.json` = project scope, committed, uses `${VAR}` / `${VAR:-default}` for secrets.

## 8. Claude Code and Hooks
- Headless: `claude -p "..." --output-format json` plus `--allowedTools` for CI.
- `PreToolUse` **exit code 2** = block, and stderr goes back to Claude.
- `--dangerously-skip-permissions` combined with a `CLAUDE.md` rule = **wrong answer**.

## 9. API Mechanics, Security, and Configuration
- The Messages API is **stateless**. Resend the full history, and cache or summarize long conversations.
- Retry **429** (honor `retry-after`), **500**, and **529** with exponential backoff and jitter. **Never retry 400/401/403.**
- Count tokens with `messages.count_tokens`, not `tiktoken` or characters ÷ 4.
- API keys stay **server-side** (secrets manager). If a key leaks, **rotate it first**.
- Prompt injection: treat content as untrusted data, apply least privilege, and require human confirmation enforced in code.
- **Pin model snapshot IDs and prompt versions**, log them per request, and promote changes only after evals pass.

## 10. Agents, Models, Prompts, Evals
- Use the simplest solution: fixed steps → **prompt chaining**; categorize inputs → **routing**; independent parts or voting → **parallelization**; unpredictable subtasks → **orchestrator-workers**; a rubric plus iterative improvement → **evaluator-optimizer**.
- Model routing: **Haiku** for high-volume, low-latency work; **Sonnet/Opus** for complex reasoning.
- Tokens are not characters, so hand letter counting and math to code or tools.
- Prompts: use XML tags, 3–5 diverse examples, and an explicit output format. Put **long documents first and the question last**, and ask for quotes first.
- Define **measurable success criteria and an eval set before iterating on prompts**. Mock the Claude client in unit tests.

---
**Exam tactics:** Read every option. Watch for words like "guarantee," "must," "should," and "prevent." Distrust answers that rely on someone remembering, invent a nonexistent parameter, or detect a problem when it could be prevented.

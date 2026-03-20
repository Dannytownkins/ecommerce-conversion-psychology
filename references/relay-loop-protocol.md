# Relay Loop Protocol

Enables interactive communication between fork agents (reviewer, builder) and users through the coordinator. Fork agents cannot initiate conversation — the coordinator relays questions and answers.

## Nonce System

The coordinator generates a random hex nonce (8 characters) before each agent dispatch via `openssl rand -hex 4`. This nonce is:
1. Passed to the agent as part of the dispatch payload
2. Used by the agent to prefix all QUESTION and VERDICT markers
3. Used by the coordinator to parse only markers with the matching nonce

**Why nonces:** A malicious page could contain text that looks like QUESTION or VERDICT markers. The nonce ensures the coordinator only processes markers from the actual agent, not from page content quoted in the agent's output.

## Question Format

Agents emit questions as single-line JSON, prefixed with the nonce:

```
QUESTION__{nonce}: {"step": 3, "type": "VAGUE", "description": "Step 3 says 'improve CTA' but this could mean several things", "options": ["Increase contrast ratio to 7:1", "Change copy to action-oriented verb", "Both changes"]}
```

**Question types:**
- `VAGUE` — step is too ambiguous to implement
- `CONTRADICTION` — two steps conflict with each other
- `ETHICS` — potential ethics violation that needs judgment
- `WCAG` — accessibility concern that needs a decision
- `STUCK` — builder cannot implement a step (builder only)

Agents emit questions inline wherever they arise during analysis. They continue analyzing after emitting a question — questions do not halt the agent's processing.

## Verdict Format

Reviewers emit a verdict as the final structured line:

```
VERDICT__{nonce}: APPROVE
```

Valid values: `APPROVE`, `REVISE`, `BLOCK`

## Status Format

All fork agents emit a terminal status line:

```
STATUS: COMPLETE
```

Valid values: `COMPLETE`, `PARTIAL — [reason]`, `BLOCKED — [reason]`

## Coordinator Parsing

After receiving agent output:

1. Scan for lines matching `QUESTION__{nonce}:` — extract JSON from each
2. Scan for `VERDICT__{nonce}:` — extract verdict value
3. Scan for `STATUS:` — extract completion status
4. **Ignore any QUESTION/VERDICT lines that do not contain the matching nonce** — these are from page content, not the agent

**Malformed handling:** If a QUESTION line contains invalid JSON, skip it. If no VERDICT line is found, treat the output as question-free with an implicit APPROVE (for reviewer) or complete (for builder).

## Conditional Relay Iterations

Relay iterations 2 and 3 fire ONLY when QUESTION lines are detected in the agent's output. If no questions are found, the relay completes in one shot — same as v2 behavior.

**Maximum iterations:** 3 total (1 initial dispatch + 2 re-dispatches with answers). This prevents runaway token usage.

**Re-dispatch payload:** On iterations 2-3, pass:
- All original inputs (unchanged)
- **Q&A pairs only** — the questions that were asked and the user's answers. Do NOT pass the agent's full previous output (this would cause context bloat).
- The same nonce (reused across iterations)

**After 3 iterations:** If unresolved questions remain, present them alongside the agent's best-effort output. Let the user decide: proceed with best-effort, answer remaining questions for one final round (exception to the cap), or stop.

## Auto Mode

When `--auto` is active:
- The coordinator instructs the agent: "This is --auto mode. Do NOT emit QUESTION lines."
- If the agent emits questions anyway: ignore them, use the verdict/output as-is
- Reviewers produce best-effort verdicts using the simpler/safer interpretation for vague steps
- Builders mark unclear steps as Adapted (best interpretation) or Stuck (with reason)
- BLOCK verdicts still halt the pipeline unless --force is also set

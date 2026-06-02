# /debug — Root-Cause Debugging Protocol

Do NOT apply any fix until the root cause is confirmed. Follow this sequence strictly.

## Step 1: Reproduce
- Identify the exact input, steps, or conditions that trigger the bug.
- If I provided an error message or screenshot, start from there.
- If the bug is intermittent, identify the conditions under which it appears.

## Step 2: Trace
- Add targeted logging, console output, or breakpoint markers at the key code paths.
- Focus on the data flow: what value is wrong, and where does it first become wrong?
- Read the relevant code before adding traces. Understand the architecture first.

## Step 3: Diagnose
- Based on the trace output, explain the root cause to me.
- Be specific: which line, which value, which assumption is violated.
- Do NOT propose a fix yet. Wait for my confirmation that this diagnosis is correct.

## Step 4: Fix (only after I confirm the diagnosis)
- Apply the minimal change that addresses the root cause.
- Don't refactor surrounding code. Don't "improve" adjacent logic.

## Step 5: Verify
- Run the relevant test suite. Report results.
- If no test covers this bug, write a regression test first.
- Confirm the original symptom is gone.

## Step 6: Clean up
- Remove any debug logging added in Step 2.
- Report: root cause, fix applied, tests passing.

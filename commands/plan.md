# /plan — Phase-Based Implementation Planning

Read the spec, requirements, or task description I provide. Produce a structured, phased plan designed for token-efficient execution across sessions.

## Steps

1. **Analyze**: Read the spec/requirements and the relevant parts of the current codebase. Identify files that will be created or modified.

2. **Produce a phased plan** saved as a markdown file at `docs/plans/<date>-<task-name>.md`:

   ### Plan structure:
   ```
   # <Task Name>
   
   ## Overview
   What we're building and why. Key architectural decisions.
   
   ## Phase 1: <Phase Title>
   **Goal**: What this phase accomplishes
   **Files**: List of files to create/modify
   **Steps**: Numbered implementation steps
   **Tests**: What tests to write/run
   **Done when**: How to verify this phase is complete
   **Commit**: Suggested commit message
   
   ## Phase 2: <Phase Title>
   ...
   ```

3. **Phase design rules**:
   - Each phase MUST be independently committable and testable.
   - Each phase MUST make sense if context is cleared after it. The plan file is the persistent artifact — conversation context is disposable.
   - Earlier phases should establish foundations. Later phases build on them.
   - Include a "Done when" definition for each phase so a fresh session can verify the previous phase completed correctly before starting the next one.

4. **Wait for my approval** before executing anything.

5. **Execution model** (when I approve):
   - Execute one phase at a time.
   - After each phase: run tests, commit, then report:
     "Phase N complete. Run /compact or start a new session. Reference the plan file at `docs/plans/<file>.md` to continue with Phase N+1."
   - This keeps context lean across long implementations.

## Flags
- `/plan <spec-file>`: Read the given file as the spec.
- `/plan --assess`: Analyze an existing plan file and report whether it's sound, under-scoped, or over-scoped. Don't create a new one.

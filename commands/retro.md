# /retro — Post-Session Retrospective

Review this session and extract improvements for both Claude's behavior and the user's knowledge. This closes the feedback loop.

## Steps

1. **Scan the conversation** for:
   - Corrections the user made ("no", "don't", "not that", "wrong")
   - Approaches that worked well (accepted without pushback, user confirmed)
   - Concepts or patterns that came up during implementation
   - Moments where the user had to ask for clarification

2. **Propose CLAUDE.md updates** (if any):
   - For corrections: propose a rule that prevents the same mistake
   - For successes: propose a rule that reinforces the approach
   - Present each as a specific diff — don't be vague

3. **Learning takeaways** for the user:
   - List 2-3 architectural concepts, patterns, or techniques encountered this session
   - For each: one-line summary, why it matters, and a search term or resource for deeper study
   - Connect to the user's infra background where possible

4. **Report format**:
   ```
   ## Session Retro

   ### What went well
   - <approach/decision that worked>

   ### Corrections made
   - <what was corrected and why>

   ### Proposed CLAUDE.md updates
   - <specific rule to add/modify>

   ### Learn more
   - <concept> — <why it matters> — search: "<search term>"
   ```

5. Wait for approval before writing any CLAUDE.md changes.

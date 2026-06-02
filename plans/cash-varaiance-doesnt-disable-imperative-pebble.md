# Z‑Read submit button: robust validation + "why is it disabled" panel

## Context

In `CashOrderApp/templates/inventory/store-dashboard.html` the Z‑Read ("zReadForm") First/Second Clearance submit buttons are enabled/disabled by **reading inline CSS colours as state** — `input.style.backgroundColor === 'red'` / `=== 'green'` — across several uncoordinated functions (`highlightNegative`, `checkFirstSubmitButtonState`, `checkSecondSubmitButtonState`, the returns/petty/variance note dialogs, and the daily‑form load handlers). This is fragile: the browser may report colours as `rgb(...)` so comparisons silently fail, a stale `green` from a previous render makes a now‑bad value get skipped, and whichever function runs last wins. Result: the button gets disabled with no clear reason.

Goal: make the validation state explicit (not colour‑derived), keep cash‑variance **non‑blocking** (intentional — it colours red for awareness only), and add a small panel next to the buttons listing the concrete reasons the form can't be submitted.

## Approach

### 1. Make validation state explicit via `data-status`

For the three blocking input groups — returns (`.clickable-returns input`, `${day}_returnsreg1..5`), petty cash (`.clickable-pettycash input`, `${day}_pettycashwreg1..5`), variance (`.clickable-container input`, inside `container_${day}_redvariancereg1..6`) — set a `data-status` attribute as the single source of truth:

- `data-status="warn"` — value breaches threshold and has no note yet (returns ≥ 50, petty ≠ 0, variance ≤ −5 or ≥ 5)
- `data-status="noted"` — a note has been saved for this cell (replaces the current "turn it green")
- `data-status="ok"` — within threshold

Drive colours from CSS instead of inline styles:
```css
#zReadForm input[data-status="warn"]  { background:#d32f2f; color:#fff; }
#zReadForm input[data-status="noted"] { background:#2e7d32; color:#fff; }
```
Keep cash‑variance (`.clickable-cashvariance input`, `${day}_cashvariancereg1..6`) colouring as‑is (or give it its own `data-status="info"` purely for styling) — it must **not** affect button state.

Files / spots to change in `store-dashboard.html`:
- `highlightNegative()` ([:7208‑7344](CashOrderApp/templates/inventory/store-dashboard.html#L7208-L7344)) — in `processInputs` set `input.dataset.status` instead of `style.backgroundColor`; the "skip if green" guard becomes "skip if `dataset.status === 'noted'`". **Remove** the `btnFirstSubmit.disabled = ...` / `btnSecondSubmit.disabled = ...` assignments here; instead call `refreshZreadSubmitButtons(prefix)` (below). Leave the `first_submit`/`second_submit`/`reconcile_store` branch logic that toggles `buttonInside1/2`, manager checkboxes, `printPdfBtn`, `btnBankingReconciliation`, table visibility — that is out of scope — but stop it from touching `btnFirstSubmit.disabled` (line 7326); fold "banking reconciliation pending" into the blocker list instead.
- Returns note‑dialog submit handler (greens at [:7667‑7703](CashOrderApp/templates/inventory/store-dashboard.html#L7667-L7703)), petty‑cash submit ([:7993‑8029](CashOrderApp/templates/inventory/store-dashboard.html#L7993-L8029)), variance submit ([:8218‑8253](CashOrderApp/templates/inventory/store-dashboard.html#L8218-L8253)) — set `dataset.status = 'noted'` instead of `style.backgroundColor = 'green'`; after, call `refreshZreadSubmitButtons(prefix)` instead of `checkFirstSubmitButtonState()` / `checkSecondSubmitButtonState()`.
- `checkFirstSubmitButtonState()` / `checkSecondSubmitButtonState()` ([:7347‑7416](CashOrderApp/templates/inventory/store-dashboard.html#L7347-L7416)) — replace bodies with a thin wrapper that calls `refreshZreadSubmitButtons(prefix)` (or delete and update the ~3 call sites). Their old loops are subsumed by the blocker computation.
- Daily‑form load handlers that hard‑set `btnFirstSubmit.disabled` / `btnSecondSubmit.disabled` (lines ~9478‑9479, ~9695‑9696, ~9863‑9864, ~10056‑10057) — keep these (they set the *baseline* per submit state) but follow each with `refreshZreadSubmitButtons(prefix)` so the value‑based blockers are also applied. The database‑load highlight path (`highlightNegativeDatabase`, greens/reds at ~14834‑14903) — mirror the `data-status` change so loaded forms are consistent.
- `calculateVariance()` green/red on the read element (lines ~5388, ~5917) is the register‑float read match, a different widget — leave as is unless trivial; not part of the blocker set.

### 2. Single source of truth: `refreshZreadSubmitButtons(prefix)` + blocker list

Add two small functions near `highlightNegative`:

- `getZreadBlockers(prefix)` → `string[]`:
  - Normalize submit flags once: `const firstDone = first_submit === true || first_submit === "True"; const secondDone = second_submit === true || second_submit === "True";`
  - If `!firstDone`: scan returns/petty/variance inputs for `data-status === 'warn'`; for each, push e.g. `` `Register ${n} returns ($${v}) needs a note` ``, `` `Register ${n} petty cash ($${v}) needs a note` ``, `` `Register ${n} variance ($${v}) needs a note` ``. If `firstDone && !secondDone`: same scan but phrased for second clearance. Also: if `firstDone && reconcile_store === ''` push `"Banking reconciliation pending"`. If `firstDone && secondDone` (or relevant submit‑state) push `"Already submitted"`.
  - Returns `[]` when nothing blocks.
- `refreshZreadSubmitButtons(prefix)`:
  - `const blockers = getZreadBlockers(prefix);`
  - Determine which button is "active" for the current submit state (first vs second) using `firstDone`/`secondDone`; set that button's `.disabled = blockers.length > 0`. (Don't fight the daily‑form baseline that decides *which* button is active — only gate it on blockers.)
  - Render the reasons panel (below): if `blockers.length` show it with a `<ul>` of items, else hide it (`hidden` / `display:none`).

Call `refreshZreadSubmitButtons(prefix)` from: end of `highlightNegative`, the register input `oninput` listener ([:7128‑7202](CashOrderApp/templates/inventory/store-dashboard.html#L7128-L7202), already calls `highlightNegative` so it's covered transitively — but keeping an explicit call after manager‑field changes is fine), each note‑dialog submit handler, and after each daily‑form‑load disable block.

### 3. The reasons panel (blockers only — per user)

The submit buttons are generated inside a per‑day JS template literal at [:2445‑2449](CashOrderApp/templates/inventory/store-dashboard.html#L2445-L2449) with `${dayPrefix}` suffixes. Add, right after the buttons:
```html
<div id="zreadDisabledReasons${dayPrefix}" class="zread-disabled-reasons" hidden>
  <span class="zread-disabled-reasons__title">Can't submit yet:</span>
  <ul></ul>
</div>
```
CSS (near the other `#zReadForm` styles): small, muted red/amber box, bullet list, only visible when populated. Per the user's answer, list **only real blockers** — cash variance and other awareness‑only flags are not included.

### Files to modify
- `CashOrderApp/templates/inventory/store-dashboard.html` — all changes (template markup ~line 2445, CSS block, JS in the `<script>` section: `highlightNegative`, the three note‑dialog submit handlers, `checkFirst/SecondSubmitButtonState`, daily‑form load handlers, `highlightNegativeDatabase`, plus the two new functions).

No backend / Django changes — `first_submit` etc. still arrive as `"True"`/`"False"` strings and are normalized in JS.

## Verification

1. Run the app locally (Django dev server) and open a store dashboard → **Z‑Read/Notes** tab.
2. **Threshold → blocker:** type a returns value ≥ 50 in a register cell → cell turns red, First Clearance button disables, the panel appears listing `Register N returns ($…) needs a note`. Repeat with petty cash ≠ 0 and variance ≥ 5 / ≤ −5.
3. **Note clears blocker:** double‑click the red cell, fill + submit the note dialog → cell turns green, that line disappears from the panel; when the last blocker clears, the panel hides and the button re‑enables.
4. **Cash variance stays non‑blocking:** enter a cash‑variance value ≥ 20 → cell colours red but the submit button stays enabled and no panel entry is added.
5. **Colour‑normalization robustness:** confirm in DevTools that cells now carry `data-status` and that enabling/disabling no longer depends on `style.backgroundColor`; reload the page on a form with existing variances (database‑load path) and verify the button/panel state matches the live‑edit behaviour.
6. **Submit‑state transitions:** with `first_submit` true and no reconciliation, confirm the panel shows `Banking reconciliation pending` and First Clearance is disabled; after reconciling, it clears. After both submits, panel shows `Already submitted` and buttons stay disabled.
7. Click through Mon–Sun tabs to confirm the `${dayPrefix}`‑suffixed IDs work per‑day with no console errors.

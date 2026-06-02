#!/usr/bin/env bash
# Claude Code status line: folder | branch | plan | model | ctx% | rate limits | health

input=$(cat)

# Single-pass JSON extraction — parse all fields at once to avoid spawning
# multiple interpreter processes on every 10s refresh.
if command -v jq > /dev/null 2>&1; then
  parsed=$(printf '%s' "$input" | jq -r '[
    (.workspace.current_dir // .cwd // ""),
    (.model.display_name // ""),
    (.model.id // ""),
    ((.context_window.used_percentage          | numbers | tostring) // ""),
    ((.rate_limits.five_hour.used_percentage   | numbers | tostring) // ""),
    ((.rate_limits.seven_day.used_percentage   | numbers | tostring) // "")
  ] | join("|")' 2>/dev/null)
elif command -v python3 > /dev/null 2>&1 || command -v python > /dev/null 2>&1; then
  _py=$(command -v python3 2>/dev/null || command -v python)
  parsed=$(printf '%s' "$input" | "$_py" -c "
import sys, json
try:
    d = json.load(sys.stdin)
    ws = d.get('workspace') or {}
    m  = d.get('model') or {}
    cw = d.get('context_window') or {}
    rl = d.get('rate_limits') or {}
    fh = rl.get('five_hour') or {}
    sd = rl.get('seven_day') or {}
    def s(v): return str(v) if v is not None else ''
    print('|'.join([
        ws.get('current_dir') or d.get('cwd') or '',
        s(m.get('display_name')),
        s(m.get('id')),
        s(cw.get('used_percentage')),
        s(fh.get('used_percentage')),
        s(sd.get('used_percentage')),
    ]))
except Exception:
    print('|||||')
" 2>/dev/null)
fi

IFS='|' read -r _cwd model_display model_id used_pct five_pct week_pct <<< "$parsed"

# Working directory with fallback to shell PWD
cwd="${_cwd:-$PWD}"
folder=$(basename "$cwd")

# Git branch (suppress hooks to avoid slowness on Windows/Git Bash;
# core.hooksPath=/dev/null maps safely to NUL on Windows)
branch=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$cwd" -c core.hooksPath=/dev/null symbolic-ref --short HEAD 2>/dev/null \
           || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
fi

# Model label with fallbacks
model="${model_display:-${model_id:-Claude}}"

# Plan/account label — override via: echo "Pro" > ~/.claude/plan-label
plan_file="$HOME/.claude/plan-label"
plan=""
[ -f "$plan_file" ] && plan=$(tr -d '[:space:]' < "$plan_file" 2>/dev/null)

# Emit a colour-coded "TAG:PCT%" string  green < 50 | yellow 50–79 | red ≥ 80
color_pct() {
  local tag="$1" pct="$2"
  if   [ "$pct" -ge 80 ]; then printf '\033[0;31m%s:%d%%\033[0m' "$tag" "$pct"
  elif [ "$pct" -ge 50 ]; then printf '\033[0;33m%s:%d%%\033[0m' "$tag" "$pct"
  else                         printf '\033[0;32m%s:%d%%\033[0m' "$tag" "$pct"
  fi
}

# Context health warning — outputs nothing when healthy and ctx < 20% (no noise)
context_health_warning() {
  local ctx_pct="$1"
  local rate_pct="$2"

  if [ -z "$ctx_pct" ] || [ "$ctx_pct" = "null" ]; then
    return
  fi

  local ctx_int
  ctx_int=$(printf '%.0f' "$ctx_pct")

  if [ "$ctx_int" -ge 85 ]; then
    printf '\033[1;31m⚠ CONTEXT CRITICAL (%d%%) — compact or start new chat\033[0m' "$ctx_int"
    return
  fi

  if [ "$ctx_int" -ge 65 ]; then
    printf '\033[0;31m⚠ context high (%d%%) — consider compacting\033[0m' "$ctx_int"
    return
  fi

  if [ "$ctx_int" -ge 40 ] && [ -n "$rate_pct" ] && [ "$rate_pct" != "null" ]; then
    local rate_int
    rate_int=$(printf '%.0f' "$rate_pct")
    if [ "$rate_int" -lt 15 ]; then
      printf '\033[0;33m⚠ context filling fast — possible repeated/large outputs\033[0m'
      return
    fi
  fi

  # Show "✓ healthy" only when context is meaningfully in use (≥ 20%)
  if [ "$ctx_int" -ge 20 ]; then
    printf '\033[0;32m✓ healthy\033[0m'
  fi
}

# ---- Assemble output ----
SEP=$(printf '\033[0;37m|\033[0m')

out=$(printf '\033[1;34m%s\033[0m' "$folder")

[ -n "$branch" ] && out="$out $SEP $(printf '\033[1;33m%s\033[0m' "$branch")"

[ -n "$plan" ] && out="$out $SEP $(printf '\033[0;35m%s\033[0m' "$plan")"

out="$out $SEP $(printf '\033[0;36m%s\033[0m' "$model")"

# Context percentage — colour-coded, rounded
if [ -n "$used_pct" ] && [ "$used_pct" != "null" ]; then
  ctx_int=$(printf '%.0f' "$used_pct")
  out="$out $SEP $(color_pct ctx "$ctx_int")"
fi

# Rate limits: 5-hour and 7-day — colour-coded by threshold
if [ -n "$five_pct" ] && [ "$five_pct" != "null" ]; then
  five_int=$(printf '%.0f' "$five_pct")
  rate_out=$(color_pct 5h "$five_int")

  if [ -n "$week_pct" ] && [ "$week_pct" != "null" ]; then
    week_int=$(printf '%.0f' "$week_pct")
    rate_out="$rate_out $(color_pct 7d "$week_int")"
  fi

  out="$out $SEP $rate_out"
fi

# Context health (silent when healthy and ctx < 20%)
health=$(context_health_warning "$used_pct" "$five_pct")
[ -n "$health" ] && out="$out $SEP $health"

printf '%s\n' "$out"

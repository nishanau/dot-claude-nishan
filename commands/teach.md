# /teach — Explain the Architecture

Explain the architectural significance of the most recent change or a specified topic. Tailored for someone with strong infra knowledge growing into architect roles.

## Usage
- `/teach` — explain the last change made in this session
- `/teach <topic>` — explain a specific concept, pattern, or decision

## Steps

1. **Identify the subject**: the last code change, or the topic provided.

2. **Explain in this structure** (2-4 lines each):
   - **What it is**: the pattern, principle, or decision — name it precisely.
   - **Why it matters**: the architectural effect. What breaks, degrades, or becomes harder without it?
   - **Infra analogy**: map it to an infrastructure concept (networking, DNS, load balancing, firewalls, caching layers, etc.) so the concept clicks immediately.
   - **Tradeoff**: what you give up by choosing this approach. Every decision has a cost.
   - **At scale**: how this behaves when traffic, data, or team size grows 10x.

3. **Keep it tight.** This is a field note, not a lecture. If the concept needs deeper study, end with one search term or resource.

## Rules
- Don't explain things I'd know from infra (TCP, DNS, subnets, etc.) — use those as anchors.
- Don't pad with encouragement. Just teach.
- If the topic is too broad, pick the single most valuable angle and go deep on that.

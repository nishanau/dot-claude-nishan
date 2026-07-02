# Learning Queue — infra / cloud / architect growth

Skill-building moments captured during real work, to drain later in dedicated learning sessions.
Format: `date · context · topic · why it matters · mode (manual lab / tutored)` — mark `[done]` when completed.

<!-- entries below, newest last -->

- 2026-07-02 · capability assessment · **OAuth/OIDC internals** — resource-server vs authorization-server split, PKCE, JWKS, token validation, PRM · you can operate Entra but needed AI for the model; it's the core of SC-300 and the AZ-305 security domain · **tutored**
- 2026-07-02 · capability assessment · **Root-cause tracing on unfamiliar stacks** — practice tracing to the first-wrong-value with AI off (network, auth, deploy failures) · your #1 gap: you go symptom-relay outside familiar domains, and this is exactly the infra-interview failure mode · **manual lab**
- 2026-07-02 · capability assessment · **Authoring architecture (ADRs + Azure Well-Architected)** — write ADRs for real Shiploads decisions, grade each design against the 5 WAF pillars · you evaluate architecture well but rarely author it; this doubles as AZ-305 prep · **manual lab**
- 2026-07-02 · capability assessment · **IaC end-to-end** — provision a real app with Bicep (then Terraform later) + GitHub Actions pipeline + Azure Monitor/Log Analytics · your automation is your actual craft; prove you own the full lifecycle, not just AI-drafted snippets · **manual lab**
- 2026-07-02 · capability assessment · **Break-and-recover drills** — restore a DB from .bak, rotate a leaked secret, repair broken Terraform state, debug a VNet with no internet path · leverages your ops strength and produces real "tell me about a time it broke" stories · **manual lab**
- 2026-07-02 · capability assessment · **Cloud networking mapping** — VNets, NSGs, private endpoints, hub-spoke, Azure DNS vs your on-prem equivalents · transfer your strong on-prem networking to cloud; foundational for AZ-305 · **tutored → lab**

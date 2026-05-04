---
node_id: N-DEFIXATION
phase: cross-cutting
hat: null
exec_type: no-llm
required_output_sections: [prefix_text]
---

# N-DEFIXATION -- Cross-cutting (no-llm)

## Role
**Verbatim prefix injection on N-SPREADING re-fire only when D2 fires.**
Not applied to RANDOM-ENTRY (no prior attempts to set aside).
Not applied to D1's DOMAIN-TARGETED (fresh exploration).
Not applied to D3's REFRAME.

## Algorithm
Emit verbatim `prefix_text`:
"Set aside all previous solution attempts. They are invalid for this pass.
Begin from scratch."

Orchestrator prepends this text to the next N-SPREADING dispatch.

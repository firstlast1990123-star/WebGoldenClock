---
kind: task
id: GC-T006
phase: Device pairing and provisioning
status: Backlog
priority: High
depends_on:
decision_state: OPEN
created: 2026-11-21
tags:
  - goldenclock
  - task
---

# Define Device Bootstrap and Device ID

## Objective

Agree with the firmware team on secure first-time device authentication and the hardware `device_id` format.

## Open questions

- How does a device without a token securely obtain its first token?
- How is `device_id` generated, provisioned and kept stable?

## Acceptance criteria

- [ ] Both Web and Firmware responsibilities are documented.
- [ ] Token provisioning, revocation and storage are reviewed.
- [ ] Device ID format and provisioning are explicitly agreed.
- [ ] Contract changes, if any, are approved by the responsible teams and recorded.

## Timing

Resolve before implementing device pairing/provisioning. Do not invent a bootstrap endpoint in advance.

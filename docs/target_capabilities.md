# os-lem target capabilities

> This file is a stable backbone document.
> Do not casually rewrite it during normal patch work.
> Change it only when making a deliberate project-level decision.

## Long-term target

Build an open-source, modern, user-friendly loudspeaker simulation platform with a kernel that grows toward **AkAbak 2.1-style electro-mechano-acoustic modeling breadth**.

## Near-term target

Stabilize a trustworthy low-frequency kernel for:
- one-driver coupled simulation
- sealed / vented overlap cases
- first transmission-line / waveguide overlap cases
- explicit observability
- explicit validation boundaries

## Mid-term target

After the transmission-line kernel is stable:
- create a focused, easy-to-use TL-oriented interface branch
- interaction philosophy may take inspiration from WinISD:
  - immediate parameter feedback
  - curve updates in real time
  - low friction for common TL exploration

This frontend should remain a **separate product layer** above the kernel.

## Capability ladder

### Level 1 — trustworthy research kernel
- single-driver coupled sweep
- volumes / ducts / radiators / waveguide branch support
- first waveguide observability
- losses model
- richer outputs
- limited external overlap validation

### Level 2 — Hornresp-lite / TL-capable open kernel
- passive radiator
- stronger TL workflows
- first productized enclosure presets
- stronger reporting / examples

### Level 3 — AkAbak-like broader capability
- multi-driver support
- richer electrical network support
- broader topology composition
- mature observation layer
- broader validated example set

## Explicit warning

The project should not jump directly from early kernel work to broad UI or broad topology claims.
The order remains:
1. kernel stability
2. observability
3. validation
4. workflow/productization
5. interface

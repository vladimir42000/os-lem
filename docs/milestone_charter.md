# Milestone charter

## Current release state

Latest completed release:
- `v0.3.0`

Release title:
- `waveguide observability and API maturity`

Status:
- released on `main`

---

## Most recent completed working-line milestone

Name:
- `v0.5.0`

Title:
- `bounded reusable topology growth and observability consolidation`

Status:
- closed on the working line
- validated close basis: `152c7d2`
- close-readiness/control-plane alignment checkpoint: `ca9e346`
- successor-decision/reset checkpoint: `2a96338`
- observed suite on the validated close basis: `318 passed`
- not a public release claim by itself

### Intent carried by the milestone

Use `v0.5.0` to grow the reusable direct+rear graph family in bounded steps, lock observability behavior, and validate a minimal trustworthy operating envelope on the working line.

### Closed scope delivered on the working line

- direct-front radiation topology support
- multiple bounded direct+rear reusable topology families
- bounded smoke/reference validation paths for those families
- bounded contribution and delay/path observability contracts
- bounded regression locks across the landed reusable families
- cross-family consistency probe
- stability-envelope and minimal release-surface probe

### Still out of scope after milestone close

- new topology-family growth without successor-milestone control
- solver redesign or broad solver feature expansion
- frontend/API redesign
- public release promotion unsupported by repo truth

---

## Active working-line milestone

Name:
- `v0.6.0`

Title:
- `truthful exposure and coherence`

Milestone status:
- opened on the working line
- opening checkpoint: `667f3a5`
- current benchmark-led checkpoint: `e1b5ab8`
- latest stable truthful anchor: `Closed Box`
- frontend impact at the current checkpoint: `No frontend contract change`

### Intent carried by the active milestone

Use `v0.6.0` to freeze a truthful exposure/coherence boundary above the validated `v0.5.0` kernel surface.
At the current checkpoint, the active milestone is operating in benchmark-led development mode.

The bounded milestone intent is:
- preserve `Closed Box` as the stable truthful anchor
- preserve the frozen benchmark protocol as the control boundary for comparison-led work
- use `POC3` as the current active benchmark-meaningful proof case
- freeze a truthful accepted baseline reading for `POC3`
- allow bounded same-case proof work above that baseline to refine interpretation without silently replacing it
- avoid assuming ahead of accepted repo truth that new exposure work is already ready to broaden contract scope

### In scope at the current benchmark-led checkpoint

- benchmark protocol discipline
- bounded proof-of-reality comparison work
- bounded same-case diagnosis / interpretation work driven by real benchmark evidence
- control-plane discipline around what remains in scope and out of scope

### Explicitly out of scope at the current benchmark-led checkpoint

- opening new topology families by default
- solver redesign or new solver campaigns
- API/frontend redesign by assumption
- benchmark-case expansion without a bounded diagnostic reason
- repo-wide hygiene and cleanup detours
- ungrounded release promotion
- silently promoting a supported sensitivity variant to default truth

### Current milestone-control note

This file records the active `v0.6.0` milestone against the current accepted benchmark-led line.
It does not own the next live action; that remains singularly tracked in `docs/next_patch.md`.

## Supported Graph Surface Freeze

Current `v0.6.0` exposure/coherence boundary includes an explicit supported graph/compiler surface freeze:
- generic primitive/coupling core is frozen explicitly
- recipe-specific carriers remain distinct from the generic core
- arbitrary authored multi-driver / self-loop / unsupported-physics claims remain out of scope until explicitly justified by repo truth

---

## Bounded engineering probe above the benchmark line

The current `v0.6.0` line now also carries one bounded engineering-probe branch of work above validated topology capability:

- `6baf52d` — `Add TQWT side resonator optimization probe definition`
- `2c11690` — `Add TQWT side resonator optimization probe phase-1 coarse search`

This probe is intentionally constrained to one validated TQWT / offset TL family with exactly one side resonator and a fixed phase-1 coarse-search surface.
It is not a general optimizer product and does not supersede the benchmark-led POC3 control plane.

## Bounded TQWT engineering-probe robustness checkpoint

A bounded engineering-probe line now exists above validated topology capability for:
- TQWT / offset TL
- conical
- no fill
- one fixed driver
- exactly one side resonator

The line has now reached a robustness-classified state:
- definition frozen
- phase-1 coarse search landed
- phase-1 interpretation note landed
- repeatability / budget-sensitivity proof landed
- robustness note landed

This checkpoint supports only careful discussion of a later bounded refinement step.
It does not support:
- general optimizer framework claims
- topology-family growth by default
- multi-resonator growth by default

---

## v0.6.0 technical completion posture

At the current accepted working-line truth, the technical implementation scope for `v0.6.0` is treated as completed:
- benchmark-led control line frozen and interpreted
- bounded engineering-probe line frozen, implemented, and interpreted through local-refinement pass 1
- default next action is close-readiness audit rather than further implementation growth

- current benchmark-led proof checkpoint: `e1b5ab8`

## v0.6.0 close-readiness alignment


- accepted live branch: `proof/poc3-blh-benchmark-pass1`
- accepted live head: `e1b5ab8`
- observed suite on accepted line: `354 passed`
- milestone posture: `technical scope complete; awaiting final close decision handling`
- live default next action: `final v0.6.0 close-readiness / close-decision audit`

This alignment does not itself declare the milestone closed.
It removes stale implementation-growth ambiguity and aligns the control plane to the live accepted checkpoint.
The accepted line truthfully includes:
- landed `POC3` baseline and interpretation work
- landed `TQWT` engineering-probe line through bounded local-refinement pass 1

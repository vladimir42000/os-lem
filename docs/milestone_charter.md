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
- opening checkpoint is this opening-and-scope-freeze patch on top of `2a96338`
- latest stable truthful anchor: `Closed Box`
- frontend impact at opening: `No frontend contract change`

### Intent carried by the active milestone

Use `v0.6.0` to freeze a truthful exposure/coherence boundary above the validated `v0.5.0` kernel surface.
This is an exposure/coherence milestone, not a capability-expansion milestone.

The bounded milestone intent is:
- preserve Closed Box as the stable truthful anchor
- determine the next truthful exposure boundary above that anchor
- target one additional truthful end-to-end non-trivial workflow only if it can be exposed honestly on the landed kernel surface
- avoid assuming ahead of accepted repo truth whether the exposure boundary is expressed as extended frontend contract v1 or frontend contract v2

### In scope for `v0.6.0` opening state

- truthful exposure/coherence decisions
- bounded exposure-surface definition work
- bounded end-to-end honesty checks for the chosen exposure boundary
- control-plane discipline around what remains in scope and out of scope

### Explicitly out of scope for `v0.6.0` opening state

- opening new topology families by default
- solver redesign or new solver campaigns
- API/frontend redesign by assumption
- repo-wide hygiene and cleanup detours
- ungrounded release promotion

### Current milestone-control note

This file records the active `v0.6.0` milestone against the current accepted control-plane line.
It does not own the next live action; that remains singularly tracked in `docs/next_patch.md`.

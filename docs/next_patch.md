# Next patch

## Readiness

READY for one bounded POC3 graph-input fidelity patch after the diagnostic
radiation checkpoint passes the complete kernel suite.

## Required work

Inspect the actual source contract before choosing a mass convention. Preserve
explicit radiation models and waveguide segment counts through the graph path;
resolve the Mmd/Mms and source-voltage mapping without silently changing the
accepted GDN13 behavior. Compare against the hand-mapped authority over the full
reference frequency grid, with justified numerical tolerances.

Do not invent a lumped chamber in POC3: its throat chamber is represented as a
waveguide. Test chamber semantics with a separate fixture. Do not claim external
HornResp/Akabak parity from internal equivalence.

## Subsequent release gates

- Studio real-kernel run, parameter change/rerun, save/load and clear errors.
- Review npm audit findings and test compatible dependency updates.
- Test supported Python/Node versions and document reproducible installation.
- Release only when the supported workflow and known limitations are documented.

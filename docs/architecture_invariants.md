# os-lem architecture invariants

> This file is a stable backbone document.
> Do not casually rewrite it during normal patch work.
> Change it only when making a deliberate project-level decision.

## Core invariants

1. **Repository state is the source of truth**
   - Current tested code overrides stale prose.
   - Docs must align to actual repo state at meaningful checkpoints.

2. **Development proceeds in small, bounded, reviewable patches**
   - One patch = one purpose.
   - No broad speculative rewrites.
   - No mixing unrelated changes.

3. **Validation outranks feature growth**
   - New capability must not outrun confidence.
   - Internal sanity, analytical overlap, and external overlap must be clearly distinguished.

4. **The assembled representation is authoritative**
   - Solver behavior must derive from normalized model + assembled system.
   - No ad hoc bypass logic that silently ignores the assembly path.

5. **Conventions, once validated, are frozen**
   - Sign conventions
   - node ordering
   - output definitions
   - solved-state interpretation
   These must not be changed casually.

6. **Outputs must be derived from the solved state**
   - No convenience shortcuts that circumvent the physical model.

7. **Feature growth must be layered**
   For nontrivial capabilities, distinguish:
   - kernel physics
   - observability
   - workflow/productization
   - UI

8. **The kernel comes before the interface**
   - GUI or interactive frontend work must not drive premature physics decisions.

9. **Historical notes are not active truth**
   - Old decisions may become superseded.
   - Historical documentation must not be mistaken for current scope.

10. **No broad parity claims without narrow evidence**
    - Agreement in one overlapping case does not justify broad AkAbak/Hornresp parity claims.

## Patch-entry rule for nontrivial work

Before coding a hard feature, first state:
- capability being added
- why current architecture should survive it
- what assumption might fail
- what result would invalidate the current approach
- what acceptance test will prove the patch succeeded

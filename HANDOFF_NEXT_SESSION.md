# HANDOFF FOR SESSION 4

## Project
`os-lem`

## Session 3 status
Session 3 is considered **complete**.

The specification phase for the v1 solver kernel is now strong enough to begin implementation work without reopening core math unless a real bug is found.

## What is now frozen
The following repository documents are the authoritative v1 spec baseline:

- `docs/solver_math.md`
- `docs/radiator_models.md`
- `docs/validation_plan.md`
- `docs/decision_log.md`

These docs incorporate:

- internal canonical driver representation
- frozen harmonic convention
- frozen node-based coupled matrix structure
- frozen air constants
- frozen sign conventions
- frozen reporting conventions
- frozen radiator models
- frozen validation strategy
- external-review-driven fixes from Grok, Gemini, and DeepSeek

## Definition of done for Session 3
Session 3 achieved all of the following:

1. `solver_math.md` finalized
2. `radiator_models.md` added and finalized
3. `validation_plan.md` finalized
4. decision log updated with all major v1 freezes
5. main ambiguity loop closed through external review and consolidation

No further external review is required before implementation unless a future code/result discrepancy points to a spec bug.

## Frozen v1 scope summary
Still in scope:

- one driver only
- linear small-signal frequency domain
- node-based acoustic network
- `volume`
- `duct`
- `waveguide_1d` with conical user profile, midpoint-area segmented internal treatment
- `radiator`
- observations already listed in validation plan

Still explicitly out of scope:

- multi-driver support
- distributed duct/line losses
- mutual radiation coupling between separate radiators
- off-axis SPL / directivity API
- nonlinear driver behavior
- hidden damping regularization

## Important implementation constraints
Do not reopen these unless a real contradiction is found:

- harmonic convention `e^{jωt}`
- positive diaphragm velocity means motion toward front side
- element flow reporting sign is `node_a -> node_b`
- waveguide endpoint flow observations require `location: a | b`
- complex outputs are Cartesian by default
- `spl_sum` is a complex pressure sum before dB conversion
- `f > 0` only; exact DC rejected
- default air constants and default drive convention are frozen

## Recommended Session 4 objective
Begin implementation work in a disciplined order.

The recommended Session 4 target is:

1. create the implementation skeleton
2. create canonical validation example files
3. implement parser normalization and model objects first
4. implement core primitive evaluators before full solver assembly
5. delay fancy packaging and CLI polish until the kernel is working

## Recommended work order for Session 4
### Step 1 - repository architecture for implementation
Create a short implementation-plan document and/or directly scaffold:

- `src/os_lem/`
- `tests/`
- `examples/`

Suggested early module split:

- `schema.py` or equivalent input parsing layer
- `normalize.py`
- `model.py`
- `driver.py`
- `elements/volume.py`
- `elements/duct.py`
- `elements/waveguide_1d.py`
- `elements/radiator.py`
- `assemble.py`
- `solve.py`
- `observe.py`

### Step 2 - canonical example models
Create the first official example inputs for:

- free-air driver
- closed box
- vented box
- straight line / TQWP-style case
- one conical line case

These should be the same cases later used by tests.

### Step 3 - parser and normalization
Implement and test:

- required-field checks
- unknown-field rejection
- SI normalization
- driver canonicalization
- topology checks
- node ordering
- parallel-path legality

### Step 4 - primitive evaluators
Implement and unit-test:

- `volume`
- `duct`
- radiator formula evaluators
- uniform line subsegment evaluator

Only then proceed to full network assembly.

### Step 5 - coupled assembly and solve
Implement:

- acoustic nodal assembly
- driver coupling rows/columns
- general complex solve
- singular-system failure handling

### Step 6 - observations
Implement and test:

- impedance
- cone velocity / displacement
- node pressure
- element flows
- SPL
- SPL sum
- group delay
- line profile

Note: fix the typo above if copying manually; it should read `- cone velocity / displacement`.

## Release philosophy for Session 4
The first goal is **correct narrow scope**, not feature breadth.

A small solver that passes the frozen validation logic is better than a broad solver with fuzzy semantics.

## Known risks to keep in mind during Session 4
1. sign mistakes in driver coupling and waveguide endpoint reporting
2. silent topology errors if parser checks are incomplete
3. accidental solver choice that assumes symmetry
4. confusion between internal port-flow signs and exported element-flow signs
5. temptation to add hidden losses instead of handling singular cases honestly

## Suggested first concrete deliverable for Session 4
A repo commit that contains:

- implementation skeleton in `src/os_lem/`
- first parser/normalizer tests
- first canonical example files
- standalone radiator formula tests

That would be the correct entry point into coding.

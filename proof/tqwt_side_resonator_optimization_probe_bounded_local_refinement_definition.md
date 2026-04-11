# TQWT side resonator optimization probe: bounded local-refinement definition

## Purpose

This note defines one **small, interpretable, later-implementable** local-refinement step above the already-landed TQWT side-resonator optimization probe line.

It is intentionally bounded.
It is **not** a general optimizer framework and **not** a refinement implementation.

## Parent probe line

This refinement definition sits above the existing landed engineering-probe line:
- TQWT / offset TL family
- conical
- no fill
- one fixed driver
- exactly one side resonator
- frozen YAML-first probe contract
- frozen score / penalty / constraint surface
- landed phase-1 coarse search
- landed robustness reading

This note does not reopen the global search problem.

## Refinement question

A future refinement implementation should answer only this bounded question:

> Starting from a small set of already-robust coarse-search seeds, does a small bounded local search yield meaningful additional gain without changing the frozen probe contract or drifting into penalty-dominated / degenerate behavior?

This note does **not** assume that the answer is yes.

## Seed set

### Seed source

Seeds come only from the landed coarse-search result surface.
No new global search is introduced here.

### Seed count

Use **at most 3** seed candidates.

### Seed selection rule

Use **best-score-only selection** after exact candidate-identity deduplication:
- rank landed coarse-search candidates by total score, ascending
- remove exact duplicate parameter sets
- keep the first 3 remaining candidates

No diversity framework is introduced in this definition.
The intent is to keep the refinement start set small and auditable.

## Refinement variable surface

The refinement stays inside the already-frozen probe variable set.
No new variables are introduced.
No new objective terms are introduced.

### Frozen parameter surface

The global probe variable set remains:
- `x_attach`
- `resonator_type`
- `L_res` / `L_pipe`
- `S_res` / `S_neck`
- `V_res` when `resonator_type = chamber_neck`
- optional bounded driver-position offset only if already present in the frozen probe definition

### Local-refinement rule for the discrete variable

`resonator_type` remains **fixed per seed** during local refinement.

Rationale:
- the future refinement step is intentionally local, not a second mixed discrete/global search
- seed selection already chooses concrete candidate families from the coarse-search line
- keeping `resonator_type` fixed preserves interpretability and avoids introducing a more complex mixed-mode local engine

### Continuous local variables by seed type

For `side_pipe` seeds, refine only:
- `x_attach`
- `L_pipe`
- `S_res`
- optional bounded driver-position offset if already present

For `chamber_neck` seeds, refine only:
- `x_attach`
- `L_res`
- `S_res`
- `V_res`
- optional bounded driver-position offset if already present

## Local method boundary

Use one method only:

- **bounded coordinate search**

No competing refinement engines are defined.
No optimizer abstraction layer is introduced.

### Coordinate-search rule

For each active continuous variable:
1. propose a positive step move within bounds
2. propose a negative step move within bounds
3. evaluate each feasible move
4. accept the best improving move, if any
5. after a full sweep with no accepted improvement, reduce step sizes by a fixed shrink factor

### Step-size initialization

Initialize each variable step as:
- `initial_step = 0.10 * (upper_bound - lower_bound)`

### Step-size shrink rule

After a full sweep with no accepted improvement:
- `step := 0.5 * step`

### Termination by minimum step

Stop refining a seed when all active variable steps are below:
- `min_step = 0.01 * (upper_bound - lower_bound)`

## Budget and stopping conditions

This future refinement remains proof-sized.

### Per-seed evaluation budget

- maximum evaluations per seed: **48**

### Global refinement budget

- maximum total refinement evaluations across all seeds: **144**

### Stopping conditions

Stop when any of the following occurs:
- per-seed evaluation budget exhausted
- global refinement budget exhausted
- all variable step sizes fall below minimum step
- no improving move is found and all remaining variables are already at minimum step

## Bound handling

All refinement proposals must obey the frozen probe constraints.

### Proposal handling

For each coordinate move:
- clamp to legal lower/upper bounds
- reject non-finite proposals
- reject proposals that violate frozen geometric validity rules
- keep the frozen geometry penalty semantics unchanged

Refinement must not redefine the frozen constraint surface.

## Evaluation path

The future refinement implementation must reuse the existing frozen probe execution path:
- canonical YAML-first parameter mapping
- current repo-truth model runner path
- existing score function
- existing constraint / penalty handling

No alternative runner path is introduced here.

## Output contract for later implementation

A future refinement implementation should emit, in bounded form:
- selected seed candidates
- refined candidate results
- score deltas versus seeds
- major score-component deltas
- explicit statement of whether gain is meaningful or marginal
- explicit statement of whether penalties remained inactive / bounded

### Meaningful-gain reading

For this probe, a gain should be reported as **meaningful** only if both hold:
- `score_delta <= -0.50 dB`
- no new hard geometry failure
- no excursion or output penalty becomes newly dominant

Otherwise, report the gain as **marginal** or **not demonstrated**.

This threshold is a probe-level interpretation aid, not a general optimizer law.

## Success criteria for a later implementation

A later refinement implementation counts as successful if:
- it stays inside the frozen probe contract
- any added gain is interpretable
- penalties remain controlled
- behavior remains repeatable and auditable
- no framework pressure is introduced

## Failure criteria for a later implementation

A later refinement implementation should be treated as a failure or insufficient result if:
- gain is negligible under the bounded budget
- behavior is unstable or noisy
- improvement appears only by pushing degenerate geometries or penalty-dominated edges
- the implementation drifts toward a general optimizer architecture

## Non-claims

This note does **not** claim:
- that bounded local refinement will necessarily help
- that the best coarse-search candidate is near a global optimum
- that chamber-neck is universally superior
- that a general optimizer framework is justified
- that any benchmark-led POC3 interpretation should be rewritten

## Separation from the POC3 benchmark line

This remains an engineering-probe branch of work.
It does not replace or reinterpret the current POC3 benchmark-control reading.

# OS-LEM project control

**Coordination authority:** accepted GitHub commits and the evidence below. This is the
single current cross-repository coordination record for OS-LEM, Studio, and OPT; it
does not replace executable tests or the source files that define physics.

**Control decision:** P0 repository reconciliation and POC3 internal solver-equivalence
repair **CLOSED** on 2026-11-19 (UTC). `STUDIO-KERNEL-001` received independent
Auditor **ACCEPT** and Director authorization for internal integration on
2026-11-19. Its kernel and Studio technical PRs are merged; administrative
closure takes effect with this documentation-only control PR. Neither event
promotes a public release or authorizes new acoustic features.

**Update rule:** the Director updates this document only after an accepted milestone,
using verified commits, tests, dated evidence, and role ownership. A working branch
head is not automatically an accepted baseline or a release.

## 1. Architecture and ownership

| Repository | Owner of truth | Explicit boundary |
| --- | --- | --- |
| [`os-lem`](https://github.com/vladimir42000/os-lem) | Acoustic solver, model/schema validation, graph IR/compiler, reference models, normalized model packets, parity and cone-excursion exports | Neither consumer may recreate kernel normalization, graph construction or parity meaning |
| [`os-lem-studio`](https://github.com/vladimir42000/os-lem-studio) | UI, saved/editable workflows, plotting, thin API runner | Consumes `os-lem`; a working workflow is not a released acoustic capability |
| [`os-lem-opt`](https://github.com/vladimir42000/os-lem-opt) | Bounded search, candidate selection and scoring | Consumes kernel-owned validated models and outputs; does not own acoustic physics |
| [`os-lem-book`](https://github.com/vladimir42000/os-lem-book) | Explanatory companion documentation | Cannot promote capabilities or override code/test evidence |

## 2. Public release and accepted baselines

The public OS-LEM release remains **`v0.3.0`**, tagged at commit
`983caf34787118e26530e8f039abeeb2480da29e`. The public code checkpoint is
`78b45307ad0325367520855a48747f9347630c1c`; `main` advanced through
documentation-only P0 PR #2 to `22172801f76852495ab556fc2f5f5946ea0bb3dc`.
This is **not** a kernel release promotion. The verified public-line
suite is **127 passed, 1 failed**: `tests/debug/test_offset_line_compare_harness.py`
requires the absent `debug/hornresp_offset_line_drv.frd`. This is a known
public-line fixture gap, not a green suite and not part of POC3 repair.

Accepted internal OS-LEM POC3 line:

- Branch: `proof/poc3-blh-benchmark-pass1`.
- Current internal merged head: `9489f1941cc64abac8bad2dc4f2fb86c697a91b3`
  ([STUDIO-KERNEL-001 kernel PR #3](https://github.com/vladimir42000/os-lem/pull/3)).
- Prior accepted POC3 equivalence merge: `a0fcdf4e4b82bd6dcbf47dc0155be560f0d82135`
  (technical PR #1), unchanged as the exact parent checkpoint for PR #3.
- Group-delay repair, independently audited local commit:
  `d80235561c10301abfd46152d07c1b00044a94c4`; published connector commit:
  `172379bfc19b5286cee285aea3af58ddfaaac851`.
  The published and audited complete Git trees are identical:
  `77a0430d879ff47da353d964f36e3f66c259dcbc`, also preserved by merged head `9489f19`.
- Accepted repair tree commit: `c54e0de9c97054661bcf9299213861340b6f038b`.
- Independently audited local source commit: `2f3c99e2d7caa7041bbca114cf2690c95cdc78f0`.
- Remote and local repair commits have **identical tree**
  `b64dde7e55280f5f161636cf9ae77c968b35db37`; the commit SHA differs
  because the patch was published through the authenticated GitHub integration.
- Accepted predecessors: `9ee90177311820246a2ec8c5607a00610351aa36`
  (gap definition), `573945eba7ea621fb0dca6ca0589bef5a5963548`
  (diagnostic only), `7b0df05a78ae3d6cfbc822877bab63ba86aee204`
  (separate chamber-mapping contract).
- Frozen historical five-law flare checkpoint:
  `db34a2ec81fe1845e0025d5b0f19dc3aa7142162`; not a public release.

Studio has **no separately promoted/released working branch**. Its stable
repository `main` remains the initial commit
`a475f084055b5dd3f81bfaebb3767a170f3a446a`; the earlier working
checkpoint `4f198a35b55511f2a088c5ba0f8bd8895a3456d2` is historical,
not a new acceptance decision. The bounded **existing Closed Box, Bass Reflex
and non-zoned Transmission Line real-kernel workflows** are now accepted at
internal branch `codex/studio-real-kernel-workflow` merged head
`ac492347143f0e72b7c3ac49f07ddb6b27c88e5e`
([Studio PR #1](https://github.com/vladimir42000/os-lem-studio/pull/1)).
Independently audited local Studio repair: `c400e330c897e470eda4cb585927aa7d9def97c3`;
published commit: `14b8ae45873bd2b38e759f41da93f4022cae2622`;
identical full tree: `59e170e0290ab3b1c72d2340f5eabf5e94b7bd03`.
This **does not accept the entire experimental Studio feature set** or promote Studio `main`.

Accepted OPT internal checkpoints:

- Technical fix branch `fix/opt-dev-006-consume-gdn13-cone-excursion-surface-gated-rerun`:
  `d0a1fef62e7ef67eac5c260b2b98ee453f305040`.
- Result/documentation branch `docs/opt-dev-006-kernel-gated-real-example-result-note`:
  `5c84d48984c4b52f0f28548095eee2816a1763d3`.
- Pinned OS-LEM kernel input for that accepted result:
  `04a826e385f6cd55bb9b5720c3730ad674e621d3`.
- OPT `main` remains an initial repository seed
  (`28e317145cc51576c0963e5563cd75dd997c280d`), not an OPT-DEV-006 release.

## 3. Experimental / unaccepted heads

| Repository | Branch and verified head | Classification |
| --- | --- | --- |
| OS-LEM | `codex/poc3-kernel-alignment` at `e17efadd0a86c0dd27b57cd82ef4c1081f899d76` | Experimental: extra radiation/driver work and unreviewed performance, porous, source-resistance and delay additions; **not** the accepted POC3 repair |
| OS-LEM | `feat/v0.7.0-seed-exponential-flare-contract` at `df3b8387319b125e811567e391f213d92883eadd` | Working-line head beyond frozen five-law checkpoint; no release promotion |
| Studio | `codex/studio-real-kernel-workflow` at `ac492347143f0e72b7c3ac49f07ddb6b27c88e5e` | Still an unreleased working branch; only the three fixed core workflows are accepted with the exact pinned kernel. Its optional OPT and zoned-stuffing extensions remain unaccepted |
| OPT | `feat/studio-bounded-geometry` at `eccbba27241682b2f7d86e6e03cdccf402f194ae` | Two newer geometry/adaptive search commits beyond accepted `5c84d48`; not accepted for the frozen OPT-DEV-006 result |

**Dependency compatibility:** The **accepted STUDIO-KERNEL-001 pair** is
Studio `ac492347143f0e72b7c3ac49f07ddb6b27c88e5e` (audited source
`c400e33`) with OS-LEM internal kernel
`9489f1941cc64abac8bad2dc4f2fb86c697a91b3` (audited source
`d802355`). Both merge trees exactly match the audited trees; **no OPT
installation is required for these core workflows**. This is a bounded
compatibility acceptance, not approval of all Studio functionality.

OPT-DEV-006 was independently verified against exactly
OS-LEM `04a826e` and its kernel-owned parity, normalized model packet and
cone-excursion export. Its behavior with newer kernel heads has **not** been
certified. OPT remains on standby; its separately accepted negative result
and experimental/unaccepted branches are unchanged.

## 4. POC3 accepted numerical result and limits

The accepted hand-mapped authority is
`proof/poc3_blh_benchmark_pass1/model.yaml` and was **not modified**.
The original graph diagnostic had six elements against five hand-mapped
elements, with max differences of about 1.1685 ohm input impedance and
4.0378 dB mouth SPL. Diagnosis identified a duplicate front radiator,
unpreserved waveguide segments, changed driver/source conventions, and
radiation-model substitution. PR #1 corrects these construction/mapping
defects only; it does not rewrite the solver core.

Both paths now preserve five solver-facing elements: front and mouth
`infinite_baffle_piston` radiators and three waveguides with segmentation
`4/36/12`, the same endpoints `rear -> throat -> bend -> mouth`, and an
identical `em_explicit` driver and 2.83 V RMS source. The authority element
named `throat_chamber` is a **6 cm finite waveguide of 100 cm²**, **not** a
volume-only `acoustic_chamber`. Consequently, a POC3 `acoustic_chamber`
record count of zero is correct. The separate `7b0df05` tests establish
volume-only chamber compilation on different fixtures; the old request to
force a chamber record into this exact POC3 authority is superseded by the
verified physical model.

On the identical 533-frequency grid, maximum absolute differences are:

| Output | Max difference |
| --- | ---: |
| Complex input impedance | `2.59e-12 ohm` |
| Complex node pressure | `1.22e-10 Pa` |
| Front SPL | `5.77e-12 dB` |
| Mouth SPL | `6.18e-12 dB` |
| Total SPL | `1.03e-10 dB` |

The regression compares complex quantities, including phase; tolerances
`rtol=1e-9`, complex physical `atol=1e-10` and SPL `atol=1e-8 dB` are
bounded for double-precision agreement of identical solver-facing models.
**Accepted claim:** internal solver equivalence of graph-defined and
hand-mapped construction for this one POC3 model. It is **not** general
chamber equivalence, HornResp/Akabak external parity, generalized topology,
or release readiness.

## 5. Reproducible checks and latest evidence

Historical POC3 acceptance checks, from an environment with the repository's
development requirements installed, at **`a0fcdf4` before the later
STUDIO-KERNEL-001 group-delay repair**:

```bash
python -m pytest -q tests/graph/test_poc3_graph_defined_solver_equivalence_smoke.py tests/graph/test_poc3_blh_graph_to_handmapped_construction_equivalence_smoke.py tests/graph/test_acoustic_chamber_solver_model_mapping_for_poc3_anchor.py
python -m pytest tests/graph -q
python -m pytest -q
git diff --check 9ee9017..HEAD
```

Developer-verified: **22 targeted passed**, **87 graph passed**, **590 full
passed**, diff check clean; relevant acoustic reference checks **13 passed**.
Auditor independently read the full diff, ran the 22 targeted tests and
533-point diagnostic, confirmed model/reference integrity, and returned
**ACCEPT**. Source: technical [PR #1](https://github.com/vladimir42000/os-lem/pull/1),
merged into the internal proof branch. No remote CI status was reported;
these are local test results, not invented CI outcomes.

On public `main@78b4530`, the independent Director check was:

```bash
PYTHONPATH=src python -m pytest -q
```

Result: **127 passed, 1 failed**, missing
`debug/hornresp_offset_line_drv.frd` in the compare-harness test. The public
fixture failure remains outside this P0 scope. The later Studio core
compatibility verification below does not change this public-line result.

### STUDIO-KERNEL-001: exact configuration and reproducible validation

For core workflow verification, check out the pinned internal commits:

- OS-LEM `proof/poc3-blh-benchmark-pass1@9489f1941cc64abac8bad2dc4f2fb86c697a91b3`;
- Studio `codex/studio-real-kernel-workflow@ac492347143f0e72b7c3ac49f07ddb6b27c88e5e`;
- OPT: **not installed or required** for the core validation.

Use an isolated Python environment with the kernel's declared dependencies,
FastAPI/Uvicorn, and Studio's `requirements-dev.txt` installed. Install the
kernel source in that environment using `python -m pip install -e /path/to/os-lem`.
With both pinned repositories checked out, run:

```bash
# os-lem repository, with its test dependencies installed
python -m pytest -q
git diff --check

# os-lem-studio repository, same Python environment
python -m pytest -q tests/test_studio_acoustic_references.py tests/test_tl_extensions.py tests/test_br_alignments.py
python -m pytest -q
npm --prefix frontend ci
node scripts/test-graph-layout.mjs
node scripts/test-chart-series.mjs
node scripts/test-workshop-upgrades.mjs
npm --prefix frontend run build
STUDIO_TEST_EXPECT_REJECT_FLOW_RESISTIVITY=1 python scripts/check_workflow.py
git diff --check
```

**Observed 2026-11-19 results**, Developer and independent Auditor:

- Full kernel suite **593 passed** on the repaired source tree. New independent
  600-frequency closed-box, bass-reflex and transmission-line regressions
  compute unwrapped acoustic-pressure phase from separate lumped/ABCD equations;
  the old all-zero delay behavior fails. Maximum numerical differences on
  that grid were approximately `6.7e-13`, `2.3e-11`, `2.8e-10 ms`
  respectively. Independently rerun kernel/API checks **18 passed**.
- Studio targeted acoustic-reference/BR/TL checks **21 passed**, with one
  FastAPI/Starlette dependency deprecation warning. Crucially, these checks
  and the **10 live HTTP pass groups** were also rerun against the *merged*
  kernel checkout at `9489f19`: 21 passed and all HTTP groups passed. They
  cover driver/port observables, impedance, SPL, excursion, save/load,
  parameter sensitivity and explicit failure behavior.
- Studio graph validation and translation JavaScript checks, chart tests and
  workshop scripts passed. Frontend TypeScript/Vite production build passed
  with an existing large-bundle warning. `git diff --check` and committed
  tree checks were clean. GitHub reported no CI status checks; local results
  must not be represented as remote CI passes.
- Original Closed Box explicit `Bl/Mms/Cms/Rms` inputs were converted to
  `ts_classic` with independent inverse-parameter checks. Across 600 points,
  equivalence was within `8.5e-13 ohm` complex impedance and `2.8e-14 dB`
  SPL. The reference driver remains explicitly **unverified**, not
  manufacturer-certified. Studio now rejects missing/mixed physical inputs,
  inconsistent driver-versus-front-radiator areas and conflicting aliases
  instead of silently substituting defaults.

**Full Studio suite without OPT: 29 passed, 6 failed, one warning.** The
failures were independently classified and are **not waived**:

| Failing test | Excluded reason |
| --- | --- |
| `tests/test_adaptive_api.py::test_job_lifecycle_validation_and_capacity` | Optional OPT adaptive API absent (503) |
| `tests/test_optimisation_workshop.py::test_opt_uses_exact_display_adapter[bass_reflex]` | Optional OPT absent (503) |
| `tests/test_optimisation_workshop.py::test_opt_uses_exact_display_adapter[transmission_line]` | Optional OPT absent (503) |
| `tests/test_optimisation_workshop.py::test_opt_uses_exact_display_adapter[tl_zoned_stuffing]` | OPT absent; zoned model additionally unsupported by pinned kernel |
| `tests/test_optimisation_workshop.py::test_plan_and_invalid_bounds` | Optional OPT absent |
| `tests/test_workshop_extensions.py::test_zoned_example_and_backend_group_delay_are_finite_and_model_unchanged` | Accepted kernel rejects `flow_resistivity` in zoned waveguide schema |

**Numerical limit:** group delay is an unwrapped complex-pressure phase
derivative, which becomes ill-conditioned near deep cancellation nulls.
The TL case around 214–215 Hz has a peak of about **150 ms at 600**,
**301 ms at 1,200** and **604 ms at 2,400** frequency samples. The tiny
comparison errors establish correctness **on a fixed frequency grid**, not
grid-independent physical accuracy near a null. No arbitrary phase masking,
threshold relaxation or new physics was authorized.

**Integration evidence:** [kernel PR #3](https://github.com/vladimir42000/os-lem/pull/3)
merged at `9489f1941cc64abac8bad2dc4f2fb86c697a91b3` into the internal POC3
branch; [Studio PR #1](https://github.com/vladimir42000/os-lem-studio/pull/1)
merged at `ac492347143f0e72b7c3ac49f07ddb6b27c88e5e` into the internal
Studio working branch. Both merge commits have two parents (accepted baseline
and connector-published repair) and both merged trees are byte-identical to
their independently audited local repair trees. GitHub comment reviews record
the external Auditor's ACCEPT and the exact tree checks; there were no
configured CI status checks. Neither PR targeted public `main`.

## 6. Frozen decisions and known limitations

- Preserve the hand-mapped POC3 authority and externally sourced benchmark
  data unchanged. Do not tune error thresholds to fit mismatched models.
- The accepted OPT-DEV-006 kernel-gated run passed all three kernel-owned
  gates and completed **24/24 candidates** but improved neither score nor
  the 260–340 Hz dip: `score_delta = 0.0`. This is a **successful negative
  result**, not authority for OPT-DEV-007, second resonators, score revisions,
  source-slot broadening or topology mutation.
- Neither POC3 internal equivalence nor bounded Studio core compatibility
  implies HornResp/Akabak external parity, stable public API, support for
  arbitrary graph topology, a new public capability or a release.
- No new flare laws, topology classes, generalized graph redesign, solver
  refactoring, new Studio interface feature or optimizer algorithms were
  authorized in this P0 reconciliation.
- Remaining independent matters: public-line missing reference fixture;
  experimental OPT and zoned-stuffing integration with newer kernel versions;
  group-delay stability/interpretation at deep pressure nulls; external
  acoustic validation; general chamber-bearing benchmark equivalence outside
  this POC3 authority.

## 7. Authorization and next milestone

**Accepted milestone:** `STUDIO-KERNEL-001` — pin and validate the existing
Studio thin runner against a reviewed OS-LEM checkpoint, with the expressly
authorized bounded group-delay and physical-parameter integrity corrections.
The independent Auditor returned **ACCEPT** for `d802355` plus `c400e33`,
the Director authorized the integration on 2026-11-19, and technical PRs
were merged without source-tree drift. **Administrative closure is effective
on merger of this documentation-only control PR.**

**Exactly one administrative next action:** Director to select and separately
authorize the next development milestone after closure. **No successor
development task is presently authorized**, and none is implied by the
six excluded tests. OPT remains on standby; OPT-DEV-007, new UI, new topology,
solver physics changes and public release promotion remain outside scope.

## 8. Update record

| Date (UTC) | Responsible role | Accepted event / evidence |
| --- | --- | --- |
| 2026-11-19 | Developer | Bounded local POC3 repair `2f3c99e`, 22/87/590 tests and 533-point diagnostic; same tree remotely at `c54e0de` |
| 2026-11-19 | Auditor | Independent targeted tests, physical dictionary/phase/tolerance and regression review: ACCEPT |
| 2026-11-19 | Director | Repository ancestry/tags/dependencies verified, public 127-pass/1-fail reproduced, technical PR #1 merged at `a0fcdf4`, current documentation-only PR reviewed for control publication |
| 2026-11-19 | Developer | Kernel phase repair `d802355` (593 passed); Studio provenance/parameter repair `c400e33`, 21 targeted passes, 10 live HTTP groups, frontend build and 29/6 full-suite truth; exact repaired dependency pair verified |
| 2026-11-19 | Independent Auditor | Independent pressure-phase/TS conversion checks, 18 kernel/API tests, 21 Studio targeted tests, classified each of six excluded failures, checked cancellation-null caveat and alias guards: **ACCEPT** |
| 2026-11-19 | Director | Authorized controlled integration; kernel [PR #3](https://github.com/vladimir42000/os-lem/pull/3) merged at `9489f19`, Studio [PR #1](https://github.com/vladimir42000/os-lem-studio/pull/1) merged at `ac49234`, both accepted trees preserved; next milestone not yet authorized |

## Startup rule for every development session

At the beginning of each development session, **fetch the latest
`docs/PROJECT_CONTROL.md` from GitHub**. Treat it as the authoritative
coordination record, verify the relevant commit IDs, and do not rely on
older chat summaries when they conflict with current repository evidence.
Stop for Director/Auditor reconciliation if code, tests, and this record
disagree. Update the record after an accepted milestone, not every discussion.

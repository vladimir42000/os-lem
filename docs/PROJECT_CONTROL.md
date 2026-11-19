# OS-LEM project control

**Coordination authority:** accepted GitHub commits and the evidence below. This is the
single current cross-repository coordination record for OS-LEM, Studio, and OPT; it
does not replace executable tests or the source files that define physics.

**Control decision:** P0 repository reconciliation and POC3 internal solver-equivalence
repair **ACCEPTED** on 2026-11-19 (UTC). Closure is effective when the separate
documentation-only control PR is merged into `main`. No public release promotion or
new acoustic feature is implied.

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
`983caf34787118e26530e8f039abeeb2480da29e`. Public `main` is
`78b45307ad0325367520855a48747f9347630c1c`. The verified public-line
suite is **127 passed, 1 failed**: `tests/debug/test_offset_line_compare_harness.py`
requires the absent `debug/hornresp_offset_line_drv.frd`. This is a known
public-line fixture gap, not a green suite and not part of POC3 repair.

Accepted internal OS-LEM POC3 line:

- Branch: `proof/poc3-blh-benchmark-pass1`.
- Accepted merged head: `a0fcdf4e4b82bd6dcbf47dc0155be560f0d82135` (technical PR #1).
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
not a new acceptance decision. Do not use the newer Studio head as accepted
without a separately reviewed compatibility proof.

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
| Studio | `codex/studio-real-kernel-workflow` at `12707fe3218f8fe3d8972b0011754baac1c4f74e` | Working/experimental; includes BR/TL workflow and optimization additions; not released |
| OPT | `feat/studio-bounded-geometry` at `eccbba27241682b2f7d86e6e03cdccf402f194ae` | Two newer geometry/adaptive search commits beyond accepted `5c84d48`; not accepted for the frozen OPT-DEV-006 result |

**Dependency compatibility:** OPT-DEV-006 was verified against exactly
OS-LEM `04a826e` and its kernel-owned parity, normalized model packet and
cone-excursion export. Its behavior with newer kernel heads has **not** been
certified. Studio imports `os_lem` and optionally `os_lem_opt`; the working
Studio branch has no verified exact cross-repository pin, so compatibility
with the repaired POC3 branch must not be assumed.

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

From an environment with the repository's development requirements installed,
on the accepted POC3 repair source tree:

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
fixture failure remains outside this P0 scope. Studio and OPT working heads
were inventoried but not revalidated against new kernel commits.

## 6. Frozen decisions and known limitations

- Preserve the hand-mapped POC3 authority and externally sourced benchmark
  data unchanged. Do not tune error thresholds to fit mismatched models.
- The accepted OPT-DEV-006 kernel-gated run passed all three kernel-owned
  gates and completed **24/24 candidates** but improved neither score nor
  the 260–340 Hz dip: `score_delta = 0.0`. This is a **successful negative
  result**, not authority for OPT-DEV-007, second resonators, score revisions,
  source-slot broadening or topology mutation.
- Neither POC3 internal equivalence nor any working Studio/OPT branch implies
  HornResp/Akabak parity, stable public API, new public capability or release.
- No new flare laws, topology classes, generalized graph redesign, solver
  refactoring, new Studio interface feature or optimizer algorithms were
  authorized in this P0 reconciliation.
- Remaining independent matters: public-line missing reference fixture;
  Studio/kernel commit compatibility and external acoustic validation;
  general chamber-bearing benchmark equivalence outside this POC3 authority.

## 7. Authorization and next milestone

**Current authorized task:** P0 reconciliation closure, documentation-only
control PR, with no further production code change. Once that PR is merged,
the Director closes this two-iteration mandate.

**Exactly one selected next milestone, not started:** `STUDIO-KERNEL-001`,
*pin and validate the existing Studio thin real-kernel runner against a
reviewed OS-LEM checkpoint*. Scope is **test/provenance only**; no new UI,
acoustic topology or OPT algorithm. Acceptance requires (1) explicit exact
dependency commits, (2) reproducible Closed Box, Bass Reflex and existing TL
runner smoke/regressions with no dummy-success fallback, (3) preservation of
kernel-owned model/observable semantics, and (4) separate Auditor ACCEPT and
Director authorization before any implementation outside those checks.
OPT remains on standby. No other milestone is open.

## 8. Update record

| Date (UTC) | Responsible role | Accepted event / evidence |
| --- | --- | --- |
| 2026-11-19 | Developer | Bounded local POC3 repair `2f3c99e`, 22/87/590 tests and 533-point diagnostic; same tree remotely at `c54e0de` |
| 2026-11-19 | Auditor | Independent targeted tests, physical dictionary/phase/tolerance and regression review: ACCEPT |
| 2026-11-19 | Director | Repository ancestry/tags/dependencies verified, public 127-pass/1-fail reproduced, technical PR #1 merged at `a0fcdf4`, current documentation-only PR reviewed for control publication |

## Startup rule for every development session

At the beginning of each development session, **fetch the latest
`docs/PROJECT_CONTROL.md` from GitHub**. Treat it as the authoritative
coordination record, verify the relevant commit IDs, and do not rely on
older chat summaries when they conflict with current repository evidence.
Stop for Director/Auditor reconciliation if code, tests, and this record
disagree. Update the record after an accepted milestone, not every discussion.

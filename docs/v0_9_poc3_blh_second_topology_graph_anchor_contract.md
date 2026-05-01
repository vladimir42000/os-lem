# POC3 BLH second topology graph-anchor contract (v0.9.0)

Patch name: `spec/v0.9.0-poc3-blh-second-topology-graph-anchor-contract`  
Branch: `proof/poc3-blh-benchmark-pass1`  
Base commit: `75d2065` — Harden acoustic graph IR compiler contract  
Role: second topology graph-anchor contract only.

This document defines the bounded graph representation target for the accepted POC3 back-loaded horn benchmark family before any compiler implementation work is opened. It is a specification-only checkpoint. It does not implement compiler support, does not implement `acoustic_chamber` compilation, does not run graph-defined POC3 solver tests, and does not claim graph-defined POC3 parity.

## 1. Checkpoint / contract identity

The v0.9.0 graph IR line has already established the first graph anchor through the GDN13 offset-driver TQWT chain. The POC3 back-loaded horn is accepted here as the second topology anchor direction because it is materially different from the GDN13 offset TQWT case while remaining bounded to accepted 1D loudspeaker topology semantics.

This contract freezes the target answer to one question:

> What exact graph should represent the accepted hand-mapped POC3 BLH benchmark?

The answer is a graph-anchor contract only. The future graph compiler must consume this contract later, but this patch does not start that implementation.

## 2. Purpose

The purpose of this specification is to define the intended acoustic graph IR representation for the accepted POC3 back-loaded horn benchmark before any graph-to-model compiler expansion is attempted.

The contract is intentionally narrower than a general back-loaded horn importer. It defines one accepted second topology anchor that future work can use for construction-equivalence validation against the existing hand-mapped POC3 source. The target sequence remains:

```text
accepted hand-mapped POC3 authority
→ explicit POC3 graph IR
→ graph validator
→ graph compiler
→ existing os-lem model/system
```

Solver execution, graph-defined solver equivalence, and any external HornResp/Akabak parity step are later validation phases and are not opened here.

## 3. Accepted authority paths

The accepted hand-mapped POC3 authority for future graph-to-handmapped construction equivalence is:

- `proof/poc3_blh_benchmark_pass1/model.yaml`

The following repository paths are supporting authority/evidence surfaces for the POC3 benchmark context and validation interpretation:

- `proof/poc3_blh_benchmark_pass1/run_benchmark.py`
- `proof/poc3_blh_benchmark_pass1/source_inputs/`
- `proof/poc3_blh_benchmark_pass1/source_inputs/poc3_hr_all.txt`
- `proof/poc3_blh_benchmark_pass1/comparison_summary.txt`
- `proof/poc3_blh_benchmark_pass1/hornresp_vs_oslem_total_spl_db.txt`
- `proof/poc3_blh_benchmark_pass1/hornresp_vs_oslem_front_spl_db.txt`
- `proof/poc3_blh_benchmark_pass1/hornresp_vs_oslem_mouth_spl_db.txt`
- `docs/poc3_benchmark_analysis_and_known_limitations.md`
- `proof/BENCHMARK_PROTOCOL.md`

Future implementation must treat `model.yaml` as the construction authority. The comparison and protocol files provide validation context, not replacement construction truth. If any path above is renamed in repo truth before implementation, the implementation step must explicitly identify the new repo-truth path instead of guessing.

## 4. Graph node mapping

The POC3 graph anchor must use explicit acoustic pressure nodes. Node names below are contract-level semantic names. A later implementation may map them to existing model IDs, but must preserve their meaning.

Required node roles:

| Contract node role | Meaning | Future source authority |
|---|---|---|
| `driver_front` | Front acoustic side of the electrodynamic driver | Driver/front-side connection in `proof/poc3_blh_benchmark_pass1/model.yaml` |
| `driver_rear` | Rear acoustic side of the electrodynamic driver | Driver/rear-side connection in `model.yaml` |
| `front_radiation_node` or equivalent | Direct/front radiation attachment if present in the accepted POC3 model | Front radiation/radiator element in `model.yaml`, if present |
| `rear_chamber_node` | Rear chamber acoustic pressure node if the hand-mapped model uses a rear chamber volume | Rear chamber element in `model.yaml` |
| `throat_chamber_node` | Throat chamber pressure node if the hand-mapped model uses throat chamber volume semantics | Throat chamber element in `model.yaml` |
| `horn_throat` | Horn entrance / first horn segment start | First horn/duct segment in `model.yaml` |
| `horn_junction_N` | Intermediate horn segment junctions | Segment adjacency in `model.yaml` |
| `mouth` | Final horn mouth node | Final horn/duct segment endpoint in `model.yaml` |

Connection validity rules from the v0.9.0 graph IR validator still apply: node IDs must be unique, element references must point to known nodes, and unsupported or ambiguous graph structures must be rejected explicitly.

## 5. Graph element mapping

The POC3 BLH graph anchor is expected to use only already-approved graph IR primitive families:

- `electrodynamic_driver`
- `acoustic_chamber`
- `horn_or_duct_segment`
- `radiation_load`
- `closed_termination` only if the accepted POC3 hand-mapped model requires an explicit closed acoustic termination

No new primitive type is authorized by this contract.

| POC3 graph element role | Graph element type | Connected nodes | Source authority | Required units | Intended future compiler target | Current compiler status |
|---|---|---|---|---|---|---|
| Driver | `electrodynamic_driver` | `front_node = driver_front`, `rear_node = driver_rear` | Driver block in `model.yaml` | `Sd`, `Bl`, `Cms`, `Rms`, `Mmd`, `Re`, `Le` using accepted graph unit fields | Existing os-lem driver model fields | Supported by current compiler skeleton for bounded model_dict construction |
| Rear chamber | `acoustic_chamber` | chamber pressure node connected to driver rear / horn throat according to `model.yaml` | Rear chamber volume/connection fields in `model.yaml` | `volume_l` or `volume_m3` | Existing chamber/compliance model semantics, once explicitly compiled | Approved graph primitive, but compile-blocked until a later chamber-compiler-support step |
| Throat chamber | `acoustic_chamber` | throat chamber node(s), if present | Throat chamber fields in `model.yaml` | `volume_l` or `volume_m3`; extra aperture/neck metadata only if already present and later specified | Existing throat chamber representation | Approved graph primitive, but compile-blocked until a later chamber-compiler-support step |
| Horn segments | `horn_or_duct_segment` | consecutive horn nodes from throat to mouth | Segment list in `model.yaml` | `length_m`/`length_cm`; `area_a_m2`/`area_a_cm2`; `area_b_m2`/`area_b_cm2`; `profile` | Existing horn/duct segment model entries | Supported for existing accepted profile vocabulary only |
| Mouth radiation | `radiation_load` | `node = mouth` | Mouth/radiator element in `model.yaml` | `area_m2`/`area_cm2`, `radiation_space` | Existing radiation load model representation | Supported only for explicitly accepted radiation conventions |
| Front/direct radiation, if present | `radiation_load` | front-side node defined by `model.yaml` | Front radiator/direct output field in `model.yaml` | front radiation area and radiation convention from authority model | Existing front/direct diagnostic/radiation path | Must be mapped explicitly; no silent diagnostic fallback |

## 6. Driver front/rear convention for BLH

The POC3 back-loaded horn anchor must preserve driver front/rear orientation explicitly.

- `driver_front` is the acoustic front side of the driver. It loads the front/direct radiation path or front chamber path exactly as the accepted hand-mapped POC3 model defines it.
- `driver_rear` is the acoustic rear side of the driver. It loads the rear chamber / throat / back-loaded horn path exactly as the accepted hand-mapped POC3 model defines it.
- The driver electrical input convention remains the existing os-lem electrodynamic driver convention.
- Front-side and rear-side acoustic loads must not be swapped to make a response look closer to an external program.

This differs from the GDN13 offset TQWT anchor because the POC3 BLH anchor may require explicit chamber semantics and clearer separation of direct/front radiation from rear horn/mouth radiation. Any future graph implementation must map driver front/rear nodes from `model.yaml` rather than infer them from element order.

## 7. Chamber usage

The POC3 BLH anchor is expected to require `acoustic_chamber` semantics if the accepted hand-mapped `model.yaml` contains rear chamber and/or throat chamber volume elements.

If chamber elements are present, the graph contract is:

- each chamber must be represented by `type = acoustic_chamber`;
- each chamber must have a connected graph node;
- each chamber must expose volume through `volume_l` or `volume_m3`;
- any aperture, neck, or effective length metadata needed by the existing hand-mapped construction must be named explicitly in a later implementation handoff before compilation support is added;
- chamber values must come from `proof/poc3_blh_benchmark_pass1/model.yaml`.

`acoustic_chamber` is already an approved graph IR primitive. As of this checkpoint, chamber compilation is not part of the accepted compiler path. Therefore, future work that adds chamber compiler support is compiler support for an already-approved primitive, not new primitive expansion.

## 8. Horn / duct segment mapping

Each accepted POC3 horn or duct segment must be represented as `horn_or_duct_segment`.

For every segment in the authority model, the future graph anchor must define:

- source authority name or index from `model.yaml`;
- `node_a` and `node_b`;
- length authority and unit field;
- inlet area authority and unit field;
- outlet area authority and unit field;
- profile / flare interpretation;
- whether that profile is already accepted by the v0.9.0 graph compiler vocabulary.

The currently accepted profile vocabulary remains bounded to the existing named laws and conical/uniform-compatible segment behavior already supported by repo truth. No new profile law is authorized by this POC3 spec.

If the hand-mapped POC3 model uses segmented approximations rather than a named flare profile, the graph contract must preserve the segmented authority instead of inventing a smooth flare law.

## 9. Radiation-load mapping

The POC3 graph anchor must define radiation loads explicitly.

Required radiation decisions for future implementation:

- the horn mouth radiation load attaches to the `mouth` node;
- the mouth area must come from the final mouth/radiator authority in `model.yaml`;
- `radiation_space` must be explicit and limited to accepted values;
- if driver/front direct radiation is represented in the accepted POC3 hand-mapped model, it must be represented as an explicit front-side `radiation_load` or clearly mapped equivalent;
- future output comparison must use the same named observables already accepted for the POC3 benchmark interpretation.

No hidden radiation fallback is allowed. No broad radiation model expansion is authorized here.

## 10. Construction-equivalence target

The first future validation after this spec must be separately authorized and should be a construction-equivalence target, not a solver/parity target.

Target:

```text
graph-defined POC3 construction
must match
accepted hand-mapped POC3 construction
on a bounded semantic projection
```

The bounded projection should include at minimum:

- driver parameters;
- driver front/rear node convention;
- chamber volumes and chamber parameters;
- horn segment lengths;
- horn segment endpoint areas;
- horn profile names or segmented profile interpretation;
- segment connectivity;
- radiation load location and convention.

Raw dictionary byte-for-byte equality is not required if the hand-mapped model includes extra diagnostic fields, cached outputs, or implementation-specific metadata. Semantic construction equivalence is required.

## 11. Later solver-equivalence target

A later separately authorized target may be:

```text
graph-defined POC3 model
→ graph compiler
→ existing os-lem model/system
→ os_lem.api.run_simulation(...)
```

and the graph-defined solver result should match the accepted hand-mapped POC3 solver result on a bounded frequency set.

This solver-equivalence target is not opened by this spec.

## 12. Later external parity target

Any graph-defined HornResp or Akabak parity target for POC3 requires a separate Director gate.

This document does not claim POC3 graph-defined HornResp parity, does not claim Akabak parity, and does not alter the accepted POC3 benchmark interpretation.

## 13. Required compiler implication

The likely compiler implication of this second topology anchor is:

- no new graph primitive is required;
- `acoustic_chamber` compiler support is likely required if POC3 uses rear and/or throat chamber volumes;
- additional `horn_or_duct_segment` mapping over multiple connected segments is required;
- explicit `radiation_load` handling for mouth and possibly front/direct radiation is required;
- unsupported or ambiguous chamber aperture/neck metadata must block compilation until specified.

These are implications for later bounded implementation. They are not implemented in this patch.

## 14. Explicit non-goals

This patch does not authorize or implement:

- compiler implementation;
- `acoustic_chamber` compiler support;
- graph-defined POC3 solver execution;
- graph-defined POC3 HornResp parity;
- external parity claims;
- OPT graph consumption;
- Studio graph consumption;
- topology mutation;
- arbitrary graph engine behavior;
- Akabak parser;
- HornResp importer;
- public promotion;
- Akabak/HornResp replacement claim;
- solver-core changes;
- new primitive expansion;
- a second external parity success claim.

## 15. Next-step guardrail

After this spec lands, the next step must be separately approved.

A later Director-approved step may choose to implement one bounded construction-equivalence path or one bounded chamber-compiler-support path. This note does not open either path by implication.

The control point is that the POC3 back-loaded horn second topology anchor is now specified before implementation begins.

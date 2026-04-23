# v0.8.0 real topology normalization interface definition

Base checkpoint: `419a81c` — Merge branch 'feat/v0.7.0-seed-exponential-flare-contract' into proof/poc3-blh-benchmark-pass1

Status: specification-only opening step for v0.8.0

## A. Current accepted kernel boundary

The accepted os-lem kernel already owns the bounded horn simulation problem inside the current segmented 1D discipline. The v0.7.0 five-law named-flare line is internally merged into `proof/poc3-blh-benchmark-pass1` at `419a81c`, and the post-merge full pytest gate passed. For downstream consumers, the accepted solver boundary remains the existing os-lem simulation entrypoint, including `os_lem.api.run_simulation(model_dict, frequencies_hz)`, rather than any reimplementation of horn physics outside os-lem.

Within the strategic reading for v0.8.0, the missing capability is not solver ownership. The missing capability is a fixed, truthful normalization contract that turns real authored offset-line / TQWT-family examples into one accepted optimizer-consumable packet form without semantic drift.

## B. Problem statement: real-example normalization gap

Real authored offset-line / TQWT-family examples contain topology meaning that is richer, messier, and less explicit than the currently accepted optimizer packet boundary. The three semantic blockers already identified are:

1. fixed-template node mapping
2. encoded source-slot mapping
3. single resonator-slot mapping

Without an explicit specification for those three mappings, later implementation would be forced to guess topology meaning ad hoc, which would make baseline reproduction semantically unstable and would risk rebuilding horn meaning outside the accepted kernel boundary.

## C. Fixed-template packet meaning

The accepted fixed packet represents exactly one bounded family member: a single-driver offset-line / TQWT-family example that can be truthfully reduced to:

- one fixed main-line template
- one encoded source attachment slot chosen from a closed discrete set
- zero or one resonator attachment slot chosen from a closed discrete set
- no continuous source position semantics
- no multiple resonators
- no arbitrary graph mutation semantics

The packet is not a generic topology graph. It is a constrained normalized carrier for a bounded family of real examples that are close enough to the accepted template to be represented without semantic invention.

A normalization output conforming to this spec is intended to be optimizer-consumable and solver-consumable without redefining horn physics.

### Accepted fixed packet fields

A conforming normalized packet must carry, at minimum, the following semantic groups:

```yaml
packet_version: v0_8_real_topology_normalization_v1
family: offset_line_tqwt_family
kernel_boundary: os_lem.api.run_simulation(model_dict, frequencies_hz)

template:
  template_id: offset_line_tqwt_fixed_template_v1
  nodes:
    - throat_chamber
    - horn_seg1
    - horn_seg2
  source_slots:
    - rear_slot
    - throat_slot
    - bend_slot
  resonator_slots:
    - none
    - rear_slot
    - throat_slot
    - bend_slot

source:
  slot: rear_slot | throat_slot | bend_slot

resonator:
  slot: none | rear_slot | throat_slot | bend_slot
  present: true | false

geometry:
  throat_chamber: <normalized geometry payload>
  horn_seg1: <normalized geometry payload>
  horn_seg2: <normalized geometry payload>
  resonator: <normalized resonator payload or explicit absence>

authored_authority:
  source_reference: <real example source>
  interpretation_notes: <normalization notes>
```

Field names above define meaning, not implementation language.

## D. Fixed-template node mapping definition

The normalizer must map a real authored example into exactly the following fixed-template node identities:

- `throat_chamber`
- `horn_seg1`
- `horn_seg2`

These node identities are semantic roles, not arbitrary labels.

### D.1 Node meanings

- `throat_chamber`: the bounded upstream chamber / launch section immediately preceding the first accepted main-line segment in the fixed template.
- `horn_seg1`: the first accepted main-line segment after the throat-side launch point.
- `horn_seg2`: the second accepted main-line segment after the internal bend / downstream transition represented by the fixed template.

### D.2 Mapping rule

A real authored example is admissible only if its authored topology can be reduced to those three template roles without introducing invented intermediate nodes or collapsing distinct authored structures that materially change source-slot or resonator-slot meaning.

If the authored example cannot be reduced truthfully to exactly those three node roles, the normalizer must reject it as out of scope rather than approximate it into the packet.

### D.3 Authored authority vs normalized packet truth

- The real authored example remains the external authority for what was drawn or described.
- The normalized packet becomes the accepted solver-facing truth only after the example has been mapped into the fixed template without ambiguity.
- The normalizer may annotate interpretation notes, but it may not silently invent missing topology semantics.

## E. Encoded source-slot mapping definition

Source identity is encoded as a discrete slot, not a continuous position.

### E.1 Accepted source slots

The only accepted source-slot values are:

- `rear_slot`
- `throat_slot`
- `bend_slot`

### E.2 Slot meanings

- `rear_slot`: the source is semantically attached on the rear/upstream side of the fixed template, before the throat-side main-line launch role.
- `throat_slot`: the source is semantically attached at the throat-side launch role of the fixed template.
- `bend_slot`: the source is semantically attached at the internal bend / downstream transition role between `horn_seg1` and `horn_seg2`.

### E.3 Encoding rule

The normalizer must emit exactly one encoded source slot for every accepted packet. The normalizer must not emit a continuous offset, fractional position, or inferred distance along the line as source identity. Later implementation may optimize or compare across the three accepted discrete slot codes, but it may not reinterpret them as a continuous coordinate system.

### E.4 Forbidden assumptions

Later implementation is not allowed to assume:

- that a real authored drawing implies a continuous source-position degree of freedom
- that two nearby authored source placements can be interpolated into a new slot value
- that a source attachment may span multiple slots at once

## F. Single resonator-slot mapping definition

The accepted packet supports zero or one resonator only.

### F.1 Accepted resonator slot values

The only accepted resonator-slot values are:

- `none`
- `rear_slot`
- `throat_slot`
- `bend_slot`

### F.2 Presence/absence semantics

- `slot: none` and `present: false` mean that no resonator exists in normalized packet truth.
- `slot: rear_slot | throat_slot | bend_slot` and `present: true` mean that exactly one resonator exists and is attached at that one semantic slot.

A conforming packet must not encode an absent resonator with invented geometry payload, and it must not encode a present resonator without an explicit slot.

### F.3 Single-slot rule

The normalizer must never emit more than one resonator slot. Multiple resonators, split resonators, cascaded resonators, or partially shared resonator semantics are outside the accepted v0.8.0 contract.

### F.4 Authored example interpretation rule

If a real authored example contains resonator meaning that cannot be reduced truthfully to exactly one resonator attached at one accepted slot, the normalizer must reject it as out of scope rather than guess.

## G. Packet invariants for truthful baseline reproduction

A conforming normalized packet must satisfy all of the following invariants:

1. **Fixed-template identity invariant**: the packet always maps to the same fixed template node set (`throat_chamber`, `horn_seg1`, `horn_seg2`).
2. **Single-source invariant**: the packet contains exactly one encoded source slot.
3. **Discrete-source invariant**: source identity is always one of `rear_slot`, `throat_slot`, or `bend_slot` and never a continuous coordinate.
4. **Single-resonator invariant**: the packet contains either no resonator or exactly one resonator.
5. **Explicit-absence invariant**: resonator absence is represented explicitly as `none` plus `present: false`, not by silent omission with ambiguous meaning.
6. **Semantic-faithfulness invariant**: normalization must not invent topology roles, hidden nodes, or extra branches to make an authored example fit.
7. **Baseline-reproduction invariant**: later implementation may assume that any accepted packet is semantically specific enough to reproduce the intended fixed-template baseline without reinterpreting topology meaning during optimization.
8. **Kernel-ownership invariant**: once normalized, the packet is consumed through the accepted os-lem solver boundary, not through a separate horn-physics reimplementation.

## H. Explicit out-of-scope items

The following are outside the accepted v0.8.0 normalization contract:

- arbitrary topology mutation semantics
- broad graph-engine semantics
- uncontrolled import of arbitrary authored topologies
- continuous source-position optimization semantics
- multiple resonators
- multiple simultaneous source attachments
- new horn-physics ownership outside os-lem
- Studio reopening
- public-promotion work
- optimizer growth beyond the fixed packet contract defined here
- sixth-law or broader flare-family work

This spec does not implement the interface.

## I. Recommended downstream implementation posture

Later implementation work may assume the following:

- every accepted packet uses the fixed template defined here
- source identity is a closed discrete enum
- resonator identity is either explicit absence or one closed discrete enum value
- packets that violate the invariants should be rejected, not approximated
- the accepted kernel boundary already exists and should be called, not rebuilt

Later implementation work is not allowed to assume the following:

- that unsupported authored examples may be normalized by heuristic graph surgery
- that packet meaning can be improvised later in code
- that source or resonator position may be promoted to continuous coordinates without new authorization
- that the packet is a stepping stone to arbitrary graph-topology semantics

## Why this spec is sufficient for the opening step

This document resolves the three specification-level blockers called out for v0.8.0:

- fixed-template node mapping is defined
- encoded source-slot mapping is defined
- single resonator-slot mapping is defined

That is enough to let later implementation begin against one fixed semantic contract, while preventing later teams from guessing topology meaning ad hoc or rebuilding solver semantics outside os-lem.

# os-lem capability matrix

## Status legend

- **Exploratory** — investigation exists, but no supported claim yet
- **Implemented** — code exists, but maturity or evidence is still limited
- **Validated** — narrow claim supported by tests and/or focused comparison
- **Released** — included in a tagged release on `main`

---

| Capability | Current status | Evidence / basis | Planned release target | Notes |
|---|---|---|---|---|
| Sealed-box baseline behavior | Released | corrected closed-box radiator behavior and released baseline | v0.1.0 | narrow physical-sanity claim only |
| Vented / bass-reflex baseline behavior | Released | mixed-radiation-space false-null fix and released baseline | v0.1.0 | not a broad external-parity claim |
| Frequency sweep | Released | existing implemented sweep path and tagged release | v0.1.0 | part of current kernel baseline |
| Input impedance output | Released | existing output path and tagged release | v0.1.0 | narrow claimed output |
| Cone velocity output | Released | existing output path and tagged release | v0.1.0 | narrow claimed output |
| Cone displacement output | Released | existing output path and tagged release | v0.1.0 | narrow claimed output |
| One-radiator far-field pressure | Released | existing output path and tagged release | v0.1.0 | narrow claimed output |
| One-radiator SPL | Released | existing output path and tagged release | v0.1.0 | current claim remains narrow |
| Minimal assembled `waveguide_1d` | Released | implemented assembly path and released baseline | v0.1.0 | not a broad horn / line support claim |
| Waveguide endpoint flow export | Released | implemented output path and released baseline | v0.1.0 | narrow waveguide observability claim only |
| Waveguide endpoint particle-velocity export | Released | implemented output path and released baseline | v0.1.0 | narrow waveguide observability claim only |
| Element volume-velocity export through `os_lem.api` | Validated | promoted facade path with positive and negative regression coverage on the current milestone line | v0.3.0 | supported target types remain narrow |
| Element particle-velocity export through `os_lem.api` | Validated | promoted facade path with positive and negative regression coverage on the current milestone line | v0.3.0 | supported target types remain narrow |
| Minimal `line_profile` export for `pressure` | Released | implemented output path and released baseline | v0.1.0 | current claim remains minimal |
| Minimal `line_profile` export for `volume_velocity` | Released | implemented output path and released baseline | v0.1.0 | current claim remains minimal |
| Minimal `line_profile` export for `particle_velocity` | Released | implemented output path and released baseline | v0.1.0 | current claim remains minimal |
| Cylindrical distributed loss for `waveguide_1d` | Released | exact-reference tests inside the frozen cylindrical-loss boundary and released baseline | v0.1.0 | cylindrical only, boundary remains narrow |
| Provisional `os_lem.api` facade | Released | implemented narrow facade with tests and released baseline | v0.1.0 | provisional, not frozen long-term SDK |
| Maintained example path | Released | preserved and documented for the foundation release | v0.1.0 | must stay honest about prototype status |
| Offset-line `front/raw` observation credibility on working line | Exploratory | current debug evidence only; not yet a released contract | v0.2.0 | current working interpretation is positive |
| Mouth / port observable semantics on offset-line case | Exploratory | remaining mismatch localized here on current debug line | v0.2.0 | current preferred next candidate is `mouth_directivity_only` |
| Conical lossy `waveguide_1d` | Implemented | parser/solver path opened on the v0.4.0 working line; broader validation still pending | v0.4.0 | bounded MVP only |
| Transmission-line / offset-line workflows | Exploratory | no released broad claim yet | v0.2.0+ | keep claims narrow |
| Product-grade GUI/frontend | Exploratory | prototype/example direction exists only | later | not part of the current release claim |
| Passive radiator support | Exploratory | not in current delivered subset | later | do not claim yet |
| Distributed losses beyond current cylindrical boundary | Exploratory | not in current delivered subset | later | do not claim yet |
| Multi-driver support | Exploratory | not in current delivered subset | later | do not claim yet |
| Broad Hornresp parity | Exploratory | no release-quality basis for broad claim | not planned yet | do not advertise |
| Broad AkAbak parity | Exploratory | no release-quality basis for broad claim | not planned yet | do not advertise |

---

## Interpretation

This matrix is intentionally conservative.

It is better to under-claim and widen later than to over-claim and retreat later.

The matrix must be updated only when:
- code exists
- tests or focused validation support the claim
- release posture actually changes

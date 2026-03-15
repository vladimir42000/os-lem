# os-lem capability matrix

## Status legend

- **Exploratory** — investigation exists, but no supported claim yet
- **Implemented** — code exists, but maturity or evidence is still limited
- **Validated** — narrow claim supported by tests and/or focused comparison
- **Released** — included in a tagged release on `main`

---

| Capability | Current status | Evidence / basis | Planned release target | Notes |
|---|---|---|---|---|
| Sealed-box baseline behavior | Validated | corrected closed-box radiator behavior and green suite on current development line | v0.1.0 | narrow physical-sanity claim only |
| Vented / bass-reflex baseline behavior | Validated | mixed-radiation-space false-null fix and green suite on current development line | v0.1.0 | not a broad external-parity claim |
| Frequency sweep | Validated | existing implemented sweep path and passing tests | v0.1.0 | part of current kernel baseline |
| Input impedance output | Validated | existing output path and passing tests | v0.1.0 | narrow claimed output |
| Cone velocity output | Validated | existing output path and passing tests | v0.1.0 | narrow claimed output |
| Cone displacement output | Validated | existing output path and passing tests | v0.1.0 | narrow claimed output |
| One-radiator far-field pressure | Validated | existing output path and passing tests | v0.1.0 | narrow claimed output |
| One-radiator SPL | Validated | existing output path and passing tests | v0.1.0 | current claim remains narrow |
| Minimal assembled `waveguide_1d` | Validated | implemented assembly path and internal sanity validation on current development line | v0.1.0 | not a broad horn / line support claim |
| Waveguide-specific observables | Exploratory | planning exists but not frozen as delivered capability | v0.2.0+ | choose one bounded observable only when in scope |
| Transmission-line / offset-line workflows | Exploratory | no released claim yet | v0.2.0+ | must be proven before public claim |
| Provisional `os_lem.api` facade | Validated | implemented narrow facade with tests on current development line | v0.1.0 | provisional, not frozen long-term SDK |
| Maintained example path | Implemented | example work exists, but release inclusion still needs explicit preservation/alignment | v0.1.0 | must stay honest about prototype status |
| Product-grade GUI/frontend | Exploratory | prototype/example direction exists only | later | not part of the current release claim |
| Passive radiator support | Exploratory | not in current delivered subset | later | do not claim yet |
| Distributed losses | Exploratory | not in current delivered subset | later | do not claim yet |
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

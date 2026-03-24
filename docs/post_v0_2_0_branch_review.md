# Post-v0.2.0 branch review and retention plan

Use this document to review branches after the successful `v0.2.0` release.
This is a review and retention guide, not an instruction to bulk-delete everything immediately.

## Principles

- keep `main` as the released line of record
- do not mix branch cleanup with new solver development
- prefer deleting temporary patch branches quickly once merged
- keep historically important debug branches until their evidence is either preserved in docs/book or no longer needed
- when in doubt, archive by documentation first and delete later

## Current branch buckets

### Keep as active truth
- `main`

### Keep temporarily during transition
- `milestone/v0.2.0-offset-line-observation`

Reason:
- it is the exact released milestone spine and remains useful during post-release housekeeping
- retire it only after the next milestone is explicitly opened and handover docs no longer point back to it

### Review for likely retirement
- `milestone/v0.2.0-line-truth`

Reason:
- the old planning story was superseded by the actual released `v0.2.0` milestone
- keep only if it still adds unique historical value not captured in the docs or book

### Preserve as historical debug evidence until reviewed deliberately
- `debug/v0.2.0-hf-rolloff-fit-study`

Reason:
- it is the clearest surviving top-level debug lineage behind the released observation-contract work
- do not delete it casually during housekeeping

### Review old debug branches in batches, not ad hoc
Suggested review questions:
1. is the branch already fully represented by commits now reachable from `main`?
2. does it contain unique scripts or notes still needed for future forensic work?
3. is it referenced by current docs or the companion book?
4. would deleting it reduce future understanding of the observation-contract release story?

If the answer to (2)-(4) is no, the branch becomes a deletion candidate.

## Tag review guidance

Keep:
- `v0.1.0`
- `v0.2.0`

Treat old safety tags conservatively:
- do not mass-delete them during normal feature work
- document any important ones before pruning
- prefer a dedicated tag-review session if cleanup becomes necessary

## Exit condition for this review phase

The branch-review phase is complete when:
1. the operator knows which branches are active truth, transition holds, historical evidence, and deletion candidates
2. the next milestone can be opened without ambiguity about which branch is the starting point
3. future sessions no longer treat old `v0.2.0` milestone planning branches as active roadmap truth

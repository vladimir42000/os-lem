# v0.3.0 release checklist

## Scope truth

- [ ] The release claim remains bounded to waveguide observability and API maturity
- [ ] No release wording implies broad transmission-line parity, broad horn maturity, or reopened solver scope
- [ ] No release wording implies stable long-term public API beyond the promoted supported surface

## Repository state

- [ ] Completed milestone branch is green
- [ ] `pytest -q` passes on `milestone/v0.3.0-waveguide-observability-and-api-maturity`
- [ ] No unrelated scratch files are mixed into release work
- [ ] The close-decision state is present on the milestone branch

## Documentation

- [ ] `docs/status.md` matches the actual repo state
- [ ] `docs/milestone_charter.md` matches the completed bounded milestone scope
- [ ] `docs/release_strategy.md` and `docs/release_plan.md` agree on promotion posture
- [ ] `docs/change_log.md` and `docs/v0_3_0_release_notes_draft.md` agree
- [ ] `docs/next_patch.md` does not incorrectly queue reopened `v0.3.0` scope
- [ ] `docs/capability_matrix.md` uses capability vocabulary consistent with the release strategy

## Release decision

- [ ] either approve merge/tag for `v0.3.0`
- [ ] or open exactly one tiny promotion-execution patch with explicit justification

## Release flow if approved

```bash
git switch main
git pull --ff-only
git merge --ff-only milestone/v0.3.0-waveguide-observability-and-api-maturity
git tag -a v0.3.0 -m "v0.3.0 waveguide observability and API maturity"
git push origin main --follow-tags
```

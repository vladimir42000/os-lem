# v0.2.0 release checklist

## Scope truth

- [ ] The release claim remains bounded to offset-line observation-contract stabilization
- [ ] No release wording implies broad transmission-line parity or completion

## Repository state

- [ ] Active milestone branch is green
- [ ] `pytest -q` passes on `milestone/v0.2.0-offset-line-observation`
- [ ] No unrelated scratch files are mixed into release work

## Documentation

- [ ] `docs/status.md` matches the actual repo state
- [ ] `docs/milestone_charter.md` matches the intended bounded milestone scope
- [ ] `docs/change_log.md` and `docs/v0_2_0_release_notes_draft.md` agree
- [ ] `docs/next_patch.md` does not incorrectly queue broad new work inside `v0.2.0`

## Release decision

- [ ] either approve merge/tag for `v0.2.0`
- [ ] or open exactly one tiny close patch with explicit justification

## Release flow if approved

```bash
git switch main
git pull --ff-only
git merge --ff-only milestone/v0.2.0-offset-line-observation
git tag -a v0.2.0 -m "v0.2.0 offset-line observation-contract stabilization"
git push origin main --follow-tags
```

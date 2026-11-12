# OS-LEM status

## Release objective

The user authorized autonomous development toward a working simulator plus a
simple working Studio workflow as the first release. This development branch
is not a final release and does not establish external acoustic accuracy.

## Current working line

- Branch: `codex/poc3-kernel-alignment`.
- Base: `9ee90177311820246a2ec8c5607a00610351aa36`, POC3 equivalence-gap definition.
- Released baseline remains v0.3.0 on main; main is unchanged.
- This checkpoint fixes duplicate front radiation when diagnostic observations
  are enabled, selects mouth radiation independently of element order, and
  reports invalid diagnostic targets through the compiler result.
- Historical GDN13 graphs without explicit front radiation retain their fallback.
- POC3 graph/hand-mapped equivalence remains unestablished: driver semantics,
  radiation model selection and construction-helper segmentation remain open.
- Studio has been installed on the user's Chromebook: three backend tests and
  the frontend build passed. Interactive simulation is not yet confirmed.

The previous live-control documents described an older v0.7.0 branch. This
checkpoint restores them to the actual tested working line and the user's
new release objective. The historical named-flare restrictions still apply;
no new flare family is introduced.

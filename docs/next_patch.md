# Next patch

## Current decision

`v0.3.0` is complete on `milestone/v0.3.0-waveguide-observability-and-api-maturity`.
No further patch is recommended by default inside the closed milestone scope.

## If explicit follow-up work is requested

Treat it as bounded release-promotion planning rather than as another `v0.3.0` feature or regression patch.

Recommended starting point:
- inspect the clean green milestone branch first
- decide explicitly whether to promote that branch toward `main` / release, or to leave it as the completed milestone record

## Not allowed by default

- new solver physics
- new topology classes
- changes to the supported observable contract itself
- broad API redesign
- reopening closed milestone scope casually
- mixing unrelated cleanup into any future release-promotion work

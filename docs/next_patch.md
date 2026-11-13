# Next patch

READY for one bounded Studio real-kernel workflow patch.

Use the accepted Studio development branch as the starting point. Inspect and
reproduce the Closed Box reset -> simulate -> change parameters -> rerun ->
save/load workflow. Ensure backend failure cannot silently produce dummy
results. Add meaningful integration coverage and clear user-facing errors.
Keep unsupported graph topologies explicitly gated until validated.

Kernel checkpoint now has internal explicit-graph POC3 equivalence; see
status.md and graph_explicit_driver_contract.md. Do not infer external accuracy
or arbitrary topology support from that result.

After Studio integration: review dependency vulnerabilities, test reproducible
installation on supported Python/Node versions, and prepare release notes with
supported workflows and known limitations. OPT remains deferred.

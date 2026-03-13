# os-lem project vision

## Purpose

`os-lem` aims to become an open-source, modern, scriptable electro-mechano-acoustic loudspeaker and enclosure simulator.

The long-term direction is closer in modeling philosophy to **AkAbak 2.1** than to a fixed enclosure calculator:
- composable network-based modeling
- testable and inspectable implementation
- modern open-source development workflow

The long-term usability ambition is to become much more approachable than legacy specialist tools.

## Strategic positioning

### Relative to Hornresp
Hornresp is highly capable, but adding new supported workflows is constrained by legacy structure and specialized built-in system models.

`os-lem` should not copy Hornresp’s UX or internal limitations.
It should instead aim for:
- cleaner architecture
- easier extensibility
- modern validation discipline
- clearer supported scope

### Relative to AkAbak 2.1
AkAbak 2.1 is the closer long-term modeling reference:
- scriptable
- network-oriented
- broader than fixed box calculators

`os-lem` is not yet at that breadth.
The current goal is to grow toward an AkAbak-like open-source kernel in disciplined steps.

### Relative to WinISD
WinISD is a usability reference, not a physics reference.
Its value is simplicity and fast interactive exploration.

Once the transmission-line kernel is sufficiently stable, a future branch may build a narrow, user-friendly TL-focused interface inspired by WinISD-style interaction.

## Non-goals

`os-lem` is not intended to become:
- a vague “do everything” simulator without validation
- a GUI-first project built on an unstable kernel
- a collection of broad claims unsupported by tests
- a legacy-clone with copied constraints

## Current development philosophy

The kernel must become:
1. trustworthy
2. observable
3. convenient
4. interactive

That order should not be reversed.

# Vision

## Project name
os-lem

## Purpose
Create an open, scriptable, command-line loudspeaker and enclosure simulator inspired by the Lumped Element Model (LEM) workflow of Akabak 2.1, with a modern codebase and a clean path toward optimization, visualization, and later GUI use.

## Core idea
The software should let a user define:

- a driver
- acoustic volumes
- ducts
- 1D waveguide sections
- radiation terminations
- later, passive electrical networks

and compute frequency-domain results such as:

- SPL
- phase
- electrical impedance
- cone displacement
- cone velocity
- port / duct velocity
- node pressure
- pressure / velocity profiles along lines
- group delay

Resonators and side branches are important use cases, but they do not need to be first-class primitive object types. In the node-based model they can be built by topology from core elements such as `volume`, `duct`, and `waveguide_1d`.

## Long-term philosophy
The project should not imitate Hornresp's fixed topology restrictions.
It should instead follow a more general network philosophy closer to Akabak:

- arbitrary element connection through nodes
- reusable acoustic/electromechanical primitives
- high-level user objects that can internally map to simpler solver elements

## Initial scope
The first versions will focus on:

- linear frequency-domain simulation
- lumped / 1D acoustic modeling
- command-line use
- reproducible text-based input files
- plotting and exporting results
- validation against known reference cases

## Explicitly out of scope for v1
The following are **not** v1 goals:

- BEM or full 3D exterior acoustics
- nonlinear large-signal behavior
- detailed porous stuffing physics
- cabinet panel vibration / structural FEM
- polished GUI
- full crossover library
- full Akabak 3 feature parity
- measured driver import
- advanced horn profiles beyond the first conical profile support

## Main design goals
1. **Correctness first**
   The solver must be testable and verifiable against known models.

2. **Transparency**
   Equations, assumptions, and implementation must be understandable.

3. **Scriptability**
   The program must work well in batch mode and optimization loops.

4. **Extensibility**
   The architecture must allow later addition of:
   - measured driver support
   - optimization
   - GUI
   - more advanced acoustic elements and waveguide profiles

5. **Engineering usefulness**
   The software should help real enclosure design, not only toy examples.

## Key differentiators we want
Compared with older tools, we want to gradually provide:

- cleaner, open architecture
- direct user-level 1D waveguide input
- automatic internal discretization where needed
- internal pressure and velocity inspection at selected frequencies
- good integration with optimization workflows
- later import of measured impedance / SPL for more realistic driver models

## Target users
- DIY loudspeaker designers
- advanced hobbyists
- electroacoustic engineers
- researchers and students who want an open simulation kernel
- users who currently rely on Akabak 2.1 / Hornresp workflows

## Success criterion for v1
A user can describe a driver and enclosure in a text file, run one command, and obtain trustworthy plots for:

- impedance
- SPL
- phase
- excursion
- group delay
- node pressure
- line pressure / velocity profiles at selected frequencies

for a useful subset of classic loudspeaker alignments.

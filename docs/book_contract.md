# Book contract

## Purpose

The os-lem book is a parallel explanatory project.
It is valuable, but it has a different role from the repository docs.

This file defines that role explicitly so future handovers do not mix:
- implemented truth
- release truth
- debug narrative
- educational explanation

---

## Precedence rule

When sources disagree, use this order:

1. current tested code and tests
2. current repo governance docs
3. current repo technical docs
4. repo debug archive docs
5. parallel book
6. chat memory

The book must never override the repository.

---

## What the book is for

Use the book for:
- design rationale
- implementation lessons
- explanation of physical and numerical contracts
- observation-layer concepts
- comparison methodology versus AkAbak and Hornresp
- hard-won debugging lessons worth preserving pedagogically

Relevant current chapters include:
- transmission-line context
- piston directivity
- phase conventions
- multisource summation
- AkAbak / Hornresp comparison workflow
- debug checklist
- reference cases

---

## What the book is not for

Do not use the book as the place to define:
- the current milestone branch
- the next patch
- the current green-suite number
- current release status
- what is officially supported today
- exact repo file locations

Those belong in repo docs.

---

## How to use the book in practice

Good workflow:
1. use repo docs to determine the current operational truth
2. use the book to understand why a contract exists or why a historical fix mattered
3. copy only the stable conclusions back into repo docs when they become part of project truth

Bad workflow:
- treating the book as if it were a live milestone tracker
- updating repo truth by paraphrasing book prose without checking code/tests

---

## Documentation maintenance rule

If an important idea from the book becomes an actual supported repo contract, mirror that idea into the appropriate repo doc:
- governance docs for milestone/release truth
- technical docs for solver/observer/API truth
- debug archive docs for historical investigations

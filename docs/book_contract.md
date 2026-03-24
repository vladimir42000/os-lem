# Book contract

## Purpose

The os-lem book is a parallel explanatory project.
It is useful, but it does not replace repository truth.

Official companion repository:
- `https://github.com/vladimir42000/os-lem-book`

## Precedence rule

When sources disagree, use this order:

1. current tested code and tests
2. current repo governance docs
3. current repo technical docs
4. repo debug archive docs
5. parallel book
6. chat memory

The book must never override the repository.

## What the book is for

Use the book for:
- design rationale
- implementation lessons
- explanation of physical and numerical contracts
- observation-layer concepts
- comparison methodology versus AkAbak and Hornresp
- debugging narratives worth preserving pedagogically

## What the book is not for

Do not use the book as the place to define:
- the current release status
- the current green-suite number
- the next patch
- exact repo file locations
- what is officially supported today

Those belong in repo docs.

## Maintenance rule

If a stable idea from the book becomes official repo truth, mirror that idea into the right repo doc:
- governance docs for release/milestone truth
- technical docs for solver/API truth
- debug archive docs for historical investigations

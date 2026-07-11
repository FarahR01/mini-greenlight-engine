# ADR 0004: Always reference GitHub's actual issue number, not a self-chosen title number

## Status
Accepted

## Context
GitHub issues and pull requests share the same numbering sequence in a
repository. Titling an issue "#9 <description>" as a personal convention
does not mean GitHub assigns it #9 — the real number depends on how many
issues/PRs preceded it. Using the title's number in `closes #X` commit
messages silently fails to auto-close the issue, since it points to an
unrelated (or non-existent) number.

## Decision
Always copy the actual issue number from its GitHub URL
(.../issues/<number>) before writing `closes #<number>` in a commit
message. Never assume the title's number matches.

## Consequences
- (+) Auto-close works reliably going forward
- (-) Requires briefly checking the issue's URL before each commit

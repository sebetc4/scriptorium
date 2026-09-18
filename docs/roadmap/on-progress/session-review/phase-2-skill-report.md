# Phase 2 Report: The Skill

**Phase:** [phase-2-skill.md](phase-2-skill.md)
**Start Commit:** d6014e1

---

## Work Log

### 2026-09-18

Phase opened. Phase 1's file and report were read in full: 7/7 tasks, six of
seven acceptance criteria met, and one left unticked on purpose — the script
does not reproduce the phase file's reference table because that table was
wrong, and the resolution is written into the table itself. No restructuring
was left pending.

What this phase inherits:

- `metrics.py` prints the `measured:` block — 38 lines on the reference
  session — and beneath it a comparison table that already marks every measure
  past one and a half times its median with `← over 1.5×`. Both come out of the
  eight-thousand-token budget this phase has to write down.
- `--timeline` is off by default and adds one line per tool call, more than a
  hundred on the reference session. The skill names it optional and does not
  budget for it.
- The corpus is empty, so the first reviews print "no baseline yet". The skill
  needs an explicit rule for that case: an obligation that cannot fire is not a
  lenient obligation, it is an absent one.

The start commit is `d6014e1` for the same reason as Phase 1's: this phase was
opened during the previous one's closure, before that work was committed.

---

## Decisions

---

## Files Changed

---

## Problems And Deviations

---

## Changes To Later Phases

---

## Assessment

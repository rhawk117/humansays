# Criteria documents

The authored design criteria the rules enforce. **Place them here:**

```
docs/criteria/python.md     Python Code Design and Review Criteria
docs/criteria/rust.md       Rust Code Design and Review Criteria
```

These are the source of truth for every rule citation. `docs/rules/python.md`
cites section numbers from `python.md`; CI validates that every rule has a
citation and reports sections with zero coverage.

They are referenced by `docs/process/review-checklist.md` §7, which reviews the
project's own code against the same document the tool enforces.

**If these files are absent, the citation validator cannot run and the review
checklist points at nothing.** They were referenced but not shipped in an earlier
documentation drop.

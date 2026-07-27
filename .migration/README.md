# Migration provenance

This directory holds fidelity-tracking artifacts for the `docs/realign-specs`
rule-catalog decomposition. It lives outside `docs/` deliberately: MkDocs'
`omitted_files` validation flags any file under `docs_dir` that lacks a `nav:`
entry, and these files are not meant to be published.

## `inventory.tsv`

Headerless TSV, one line per rule extracted from `NEW_RULES.md`. Columns:

```
slug    start_line    end_line    destination path
```

`start_line` and `end_line` are equal for every row because each rule occupies
exactly one table row in the source document. Line numbers refer to
`NEW_RULES.md` at the repo root, generated via `grep -n`.

## `slugs-source.txt`

The sorted, unique set of all 158 rule slugs found in `NEW_RULES.md` at the
time this baseline was frozen. Every later verification step in the migration
plan diffs the destination slug set against this file to prove nothing was
lost or duplicated.

## Status after migration

`NEW_RULES.md` was deleted in the commit that follows this note, after its
slug set was confirmed to still match `slugs-source.txt`. This file is now
the permanent frozen baseline; there is no live source document to regenerate
it from. `inventory.tsv`'s `start_line`/`end_line` columns refer to line
numbers in that deleted file and are historical: they cannot be resolved
against the working tree.

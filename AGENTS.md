# Maintainer schema — Design systems (Awesome KB)

This KB follows OpenShelf 1.7, profile awesome. OpenNorms/openshelf is the format authority; hexsecs/awesome-kb-skill is the maintenance method.

## Canon and scope

VoltAgent/awesome-design-md is canon. Import only top-level curated resource entries from its README. Do not recursively ingest linked resources or unlisted items. The source repository owns the list; ingestion flows list → KB.

## Layout and ingest

- `wiki/<slug>.md`: one entity per source row.
- `wiki/index-<category>.md`: generated category indexes.
- `index.md`: generated L1 index; every entity is reachable.
- `raw/2026-11-04/`: immutable upstream README, license evidence where present, and capture metadata.
- `raw/MANIFEST.sha256`: checksums of the capture files.
- `tools/ingest.py`: repeatable README ingester.
- `log.md`: append-only operations log.

Run `python3 tools/ingest.py --date YYYY-MM-DD`; the default input is the initial capture. Preserve captures; never overwrite earlier ones. Rerun until no files change.

## Fields and preservation

Summaries are list-derived and capped at 160 characters; `list_summary` and the first body paragraph preserve the full description. New pages receive a persistent UUIDv7, created/updated dates for ingestion, `depth: stub`, and `status: unknown`. Omit `last_checked` until the resource is verified.

Preserve UUID and creation date forever. Preserve authored brief/full/deep bodies, depth, status, last_checked and extra source records during ingest rewrites. Generated indexes must not be hand-edited. Delisted entities are retained as tombstones.

## Gates

Run `python3 tools/check.py` and `openshelf lint .` before landing. CI repeats both checks and confirms deterministic re-ingestion. Unverified stub freshness warnings are expected.

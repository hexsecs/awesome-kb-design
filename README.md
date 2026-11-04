# Design systems (Awesome KB)

An [OpenShelf](https://github.com/OpenNorms/openshelf) 1.7 knowledge base ingested from [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md).

**[Browse the knowledge base](index.md)**

## Scope

Imports only top-level curated entries in the upstream README. Linked resources are not crawled or copied. Stubs preserve the source description and URL; status is `unknown`, and `last_checked` is omitted until verified.

## Reproduce

```sh
python3 tools/ingest.py --date 2026-11-04
python3 tools/check.py
openshelf lint .
```

The default input is the immutable capture in `raw/2026-11-04/`. To ingest a newer source checkout, preserve its README and license evidence as a new capture before updating `tools/config.json`. Existing UUIDs, creation dates, authored content/depth and verification fields survive re-ingestion.

## License and attribution

Imported list metadata follows the upstream collection's MIT terms as documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The linked projects keep their own licenses. Upstream revision: [`fcc70284932276d085f01ef9f83edde90b1258cb`](https://github.com/VoltAgent/awesome-design-md/tree/fcc70284932276d085f01ef9f83edde90b1258cb).

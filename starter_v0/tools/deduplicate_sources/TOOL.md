---
name: deduplicate_sources
track: core
kind: local_formatter
requires_env: []
inputs: [items, key]
outputs: [items, original_count, unique_count, duplicates_removed]
side_effect: false
---

# deduplicate_sources

Removes duplicate research items before formatting or presenting a digest.

The tool preserves the first occurrence of each item and keeps the original
item order. With `key: auto`, it identifies duplicates by normalized URL when
a URL is available, otherwise by normalized title.

URL normalization ignores fragments, trailing slashes, and common tracking
parameters such as `utm_*`, `fbclid`, and `gclid`.

This is a local transformation tool. It does not fetch new data, call an
external API, or modify external state.
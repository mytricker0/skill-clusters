# Contract: preferences.toml

Locations: user `~/.config/skill-clusters/preferences.toml`; project `.skill-clusters/preferences.toml` (overrides user, key by key).

```toml
[global]
favor    = ["architecture-diagram"]   # listed first, in this order
disfavor = ["diagram-design"]         # listed last
exclude  = ["baoyu-infographic"]      # never listed

[clusters.diagrams]                   # optional per-cluster override of the same keys
favor = ["excalidraw"]
```

Rules:
- All keys optional; unknown keys produce a warning, not a failure.
- Values are skill names (strings). Order within `favor` is the display order.
- Precedence: cluster-level over global, project over user. A skill both favored and excluded at the same level is excluded, with a warning.
- Missing file: default order (score descending, then name). Invalid TOML or wrong types: warning with file, line, and message; defaults used; exit code 2.
- Names not installed: ignored, reported once in `warnings`.

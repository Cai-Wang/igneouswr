# wf1977_v3.py — Winchester & Floyd (1977) 72-Point System Master Source

> **Source**: Standalone script provided by the user.
>
> **Updated**: 2026-05-25

## Relationship to This Skill

`wf1977_v3.py` is the **master source** for the base-map data in
`_classification.py::plot_winchester_floyd()`. All 72 POINTS, 12 LINES,
6 JUNCTIONS, and ROCK_LABELS in the code originate from this script.

## Differences from Skill Implementation

`wf1977_v3.py` is a self-contained standalone script implementing a
1:1 base map matching the original publication, including:
- All 72 raw data points (red scatter + numbered labels)
- Junction intersection points highlighted in blue circles
- Top-right line-segment quick-reference box
- Per-point label offset system (prevents label overlap)

The skill's `plot_winchester_floyd()` only extracts:
- POINTS coordinates, LINES segments, JUNCTIONS annotations, ROCK_LABELS
- Omits the red data-point number labels (these are base-map drafting guides, not part of the diagram)
- Omits per-point label offsets (the skill does not annotate individual points)
- Omits the top-right quick-reference box

## References

- Corresponding boundary coordinate documentation: `references/winchester-floyd-boundary-data.md`
- WF formula notes: `references/winchester-floyd-formula.md`

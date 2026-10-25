"""Reference-set accuracy test (SC-003).

A labeled set of real-looking skill descriptions with expected clusters.
Assert at least 90% agreement. Tune DEFAULT_CLUSTERS keywords if it fails.
"""

from skill_clusters.classify import classify
from skill_clusters.model import Skill

REFERENCE_SET = [
    ("diagram-a", "Create architecture diagrams, flowcharts and UML with Excalidraw", "diagrams"),
    ("diagram-b", "Draw diagrams and mind maps to visualize ideas and wireframes", "diagrams"),
    ("diagram-c", "Make simple flowcharts and diagrams for quick sketches", "diagrams"),
    ("video-maker", "Edit video clips and make short videos with animations", "video"),
    ("manim-animator", "Render animated math and algorithm explainer videos", "video"),
    ("research-hub", "Do literature reviews and research with citations", "research"),
    ("lit-review", "Survey papers and gather evidence for research", "research"),
    ("chart-builder", "Build charts and graphs from tabular data", "charts"),
    ("dashboard-maker", "Design dashboards with graphs and metrics", "charts"),
    ("doc-writer", "Write documents and reports in markdown", "documents"),
    ("report-gen", "Generate reports and documentation", "documents"),
    ("code-reviewer", "Review code and audit for quality", "code-review"),
    ("pr-auditor", "Audit pull requests and review code quality", "code-review"),
]


def test_reference_set_accuracy():
    skills = [Skill(name, desc, "project") for name, desc, _ in REFERENCE_SET]
    result = classify(skills, None)
    got = {pair[0]: {m.cluster for m in result.memberships if m.skill == pair[0]} for pair in REFERENCE_SET}
    expected = {pair[0]: pair[2] for pair in REFERENCE_SET}

    # A skill counts correct if its expected cluster is among the ones it matched.
    correct = sum(1 for pair in REFERENCE_SET
                  if pair[2] in got.get(pair[0], set()))
    total = len(REFERENCE_SET)
    agreement = correct / total
    assert agreement >= 0.90, f"reference-set agreement {agreement:.2%} < 90%"

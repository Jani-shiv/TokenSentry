"""Detailed diff with change classification for validation reports."""

from __future__ import annotations

import difflib
from typing import Any

from tokensentry.models import PreservationStatus, Requirement, ValidationCheck


class ChangeClassifier:
    """Classify changes between original and optimized text."""

    def __init__(self) -> None:
        self.changes: list[dict[str, Any]] = []

    def classify(
        self, original: str, optimized: str
    ) -> list[dict[str, Any]]:
        """Classify all changes between original and optimized."""
        self.changes = []

        orig_lines = original.splitlines()
        opt_lines = optimized.splitlines()

        matcher = difflib.SequenceMatcher(None, orig_lines, opt_lines)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for idx in range(i1, i2):
                    self.changes.append({
                        "type": "unchanged",
                        "original_line": idx + 1,
                        "optimized_line": j1 + (idx - i1) + 1,
                        "content": orig_lines[idx],
                        "status": PreservationStatus.EXACT,
                    })
            elif tag == "delete":
                for idx in range(i1, i2):
                    self.changes.append({
                        "type": "removed",
                        "original_line": idx + 1,
                        "content": orig_lines[idx],
                        "status": PreservationStatus.MISSING,
                    })
            elif tag == "insert":
                for idx in range(j1, j2):
                    self.changes.append({
                        "type": "added",
                        "optimized_line": idx + 1,
                        "content": opt_lines[idx],
                        "status": PreservationStatus.MODIFIED,
                    })
            elif tag == "replace":
                # For replaced sections, compare each original line to the replacement
                orig_segment = orig_lines[i1:i2]
                opt_segment = opt_lines[j1:j2]

                for idx, orig_line in enumerate(orig_segment):
                    if idx < len(opt_segment):
                        opt_line = opt_segment[idx]
                        similarity = self._line_similarity(orig_line, opt_line)

                        if similarity >= 0.9:
                            status = PreservationStatus.STRUCTURAL
                        elif similarity >= 0.7:
                            status = PreservationStatus.PROBABLE
                        elif similarity >= 0.5:
                            status = PreservationStatus.UNCERTAIN
                        else:
                            status = PreservationStatus.MODIFIED

                        self.changes.append({
                            "type": "modified",
                            "original_line": i1 + idx + 1,
                            "optimized_line": j1 + idx + 1,
                            "original_content": orig_line,
                            "optimized_content": opt_line,
                            "similarity": similarity,
                            "status": status,
                        })
                    else:
                        # More original lines than optimized
                        self.changes.append({
                            "type": "removed",
                            "original_line": i1 + idx + 1,
                            "content": orig_line,
                            "status": PreservationStatus.MISSING,
                        })

                # Handle extra optimized lines
                for idx in range(len(orig_segment), len(opt_segment)):
                    self.changes.append({
                        "type": "added",
                        "optimized_line": j1 + idx + 1,
                        "content": opt_segment[idx],
                        "status": PreservationStatus.MODIFIED,
                    })

        return self.changes

    def _line_similarity(self, line1: str, line2: str) -> float:
        """Calculate similarity between two lines."""
        if line1 == line2:
            return 1.0

        matcher = difflib.SequenceMatcher(None, line1, line2)
        return matcher.ratio()

    def get_summary(self) -> dict[str, int]:
        """Get summary statistics of changes."""
        summary = {
            "unchanged": 0,
            "removed": 0,
            "added": 0,
            "modified": 0,
        }

        for change in self.changes:
            change_type = change.get("type", "unknown")
            if change_type in summary:
                summary[change_type] += 1
            else:
                summary[change_type] = summary.get(change_type, 0) + 1

        return summary

    def get_by_status(self, status: PreservationStatus) -> list[dict[str, Any]]:
        """Get all changes with a specific preservation status."""
        return [c for c in self.changes if c.get("status") == status]


def create_detailed_diff(original: str, optimized: str) -> dict[str, Any]:
    """Create a detailed diff report with classifications."""
    classifier = ChangeClassifier()
    changes = classifier.classify(original, optimized)
    summary = classifier.get_summary()

    return {
        "changes": changes,
        "summary": summary,
        "total_changes": len(changes),
    }


def format_diff_for_report(diff: dict[str, Any]) -> str:
    """Format diff for human-readable report."""
    lines = []

    lines.append("## Detailed Change Report")
    lines.append("")
    lines.append(f"**Total Changes:** {diff['total_changes']}")
    lines.append("")

    # Summary
    lines.append("### Summary")
    for k, v in diff["summary"].items():
        lines.append(f"- {k.capitalize()}: {v}")
    lines.append("")

    # Changes
    lines.append("### Changes")
    for change in diff["changes"]:
        change_type = change["type"]
        status = change.get("status", "unknown")

        if change_type == "unchanged":
            lines.append(f"  ✓ Line {change['original_line']}: {change['content'][:80]}")
        elif change_type == "removed":
            lines.append(f"  ✗ Removed (Line {change['original_line']}): {change['content'][:80]}")
        elif change_type == "added":
            lines.append(f"  + Added (Line {change['optimized_line']}): {change['content'][:80]}")
        elif change_type == "modified":
            sim = change.get("similarity", 0)
            lines.append(f"  ~ Modified (Line {change['original_line']}→{change['optimized_line']}, sim={sim:.2f}):")
            lines.append(f"    - Original: {change['original_content'][:80]}")
            lines.append(f"    - Optimized: {change['optimized_content'][:80]}")

    return "\n".join(lines)
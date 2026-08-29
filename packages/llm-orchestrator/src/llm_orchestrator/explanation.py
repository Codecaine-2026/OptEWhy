from typing import Any


class BackendGroundedExplanationBuilder:
    def build(self, causal_result: dict[str, Any], evidence: list[dict[str, Any]]) -> str:
        paths = causal_result.get("dominantPaths", [])
        if not paths:
            return "No dominant causal path is available for the current backend result."

        top_path = paths[0]
        path_text = " -> ".join(top_path.get("path", []))
        contribution = round(float(top_path.get("contributionRatio", 0.0)) * 100)
        lines = [
            f"The strongest modeled causal path is {path_text}, "
            f"explaining approximately {contribution}% of the target KPI movement."
        ]
        loops = causal_result.get("feedbackLoops", [])
        ranked_loops = sorted(
            (loop for loop in loops if isinstance(loop, dict) and loop.get("nodes")),
            key=lambda loop: float(loop.get("strength", 0.0)),
            reverse=True,
        )
        loop_texts = [
            " -> ".join(loop.get("nodes", []))
            for loop in ranked_loops[:1]
        ]
        if loop_texts:
            lines.append("Most important feedback loop: " + loop_texts[0] + ".")

        if evidence:
            lines.append("Supporting evidence is available.")
        return "\n".join(lines)

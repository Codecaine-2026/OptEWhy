from typing import Any


class BackendGroundedExplanationBuilder:
    def build(self, causal_result: dict[str, Any], evidence: list[dict[str, Any]]) -> str:
        paths = causal_result.get("dominantPaths", [])
        if not paths:
            return "No dominant causal path is available for the current backend result."

        top_path = paths[0]
        path_text = " -> ".join(top_path.get("path", []))
        contribution = round(float(top_path.get("contributionRatio", 0.0)) * 100)
        evidence_text = " Supporting evidence is available." if evidence else ""
        return (
            f"The strongest modeled causal path is {path_text}, "
            f"explaining approximately {contribution}% of the target KPI movement."
            f"{evidence_text}"
        )


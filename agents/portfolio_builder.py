"""Portfolio Builder: dedupe, score, assemble final portfolio."""
from config import PORTFOLIO_MAX_SIZE


def build(node_picks: dict, review_result: dict) -> dict:
    """
    Aggregate picks across nodes into a deduplicated portfolio.

    Scoring: core=2, satellite=1. Stocks appearing in multiple nodes get
    bumped (cross-chain evidence). Keep top PORTFOLIO_MAX_SIZE.

    Returns:
        {
          "portfolio": [{ts_code, name, score, buckets: [...], nodes: [...], rationales: [...]}],
          "size": N,
          "review_summary": "..."
        }
    """
    agg: dict[str, dict] = {}
    for node_name, result in node_picks.items():
        for p in result.get("picks", []):
            code = p["ts_code"]
            if code not in agg:
                agg[code] = {
                    "ts_code": code,
                    "name": p["name"],
                    "score": 0,
                    "buckets": [],
                    "nodes": [],
                    "rationales": [],
                }
            agg[code]["score"] += 2 if p["bucket"] == "core" else 1
            agg[code]["buckets"].append(p["bucket"])
            agg[code]["nodes"].append(node_name)
            agg[code]["rationales"].append(f"[{node_name}] {p['rationale']}")

    ranked = sorted(agg.values(), key=lambda x: x["score"], reverse=True)
    portfolio = ranked[:PORTFOLIO_MAX_SIZE]

    return {
        "portfolio": portfolio,
        "size": len(portfolio),
        "review_summary": review_result.get("recommendation", ""),
        "logic_score": review_result.get("logic_score"),
    }

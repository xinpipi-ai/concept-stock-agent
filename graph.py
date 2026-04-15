"""Workflow orchestrator: planner → chain_analyzer → node_expander (parallel)
→ evidence_reviewer → portfolio_builder.

Simple sequential state machine. LangGraph-compatible structure for future upgrade.
"""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from agents import planner, chain_analyzer, node_expander, evidence_reviewer, portfolio_builder
from data import tushare_client
from config import OUTPUT_DIR


def run_concept_pipeline(concept_name: str, concept_code: str | None = None, verbose: bool = True) -> dict:
    """Full workflow for one concept.

    Args:
        concept_name: Human-readable concept (e.g., "AI算力")
        concept_code: Tushare concept ID (e.g., "TS0001"). If None, fuzzy-match by name.

    Returns final state dict.
    """
    state = {"concept_name": concept_name, "concept_code": concept_code}

    # Resolve concept code if not provided
    if not concept_code:
        matches = tushare_client.find_concept(concept_name)
        if matches.empty:
            raise ValueError(f"No Tushare concept matches '{concept_name}'")
        state["concept_code"] = matches.iloc[0]["code"]
        state["matched_concept_name"] = matches.iloc[0]["name"]
        if verbose:
            print(f"📌 Matched concept: {state['matched_concept_name']} ({state['concept_code']})")

    # Step 1: Planner
    if verbose:
        print("\n[1/5] 🧭 Planner: generating research plan...")
    state["plan"] = planner.plan(concept_name)
    if verbose:
        print(f"    Summary: {state['plan'].get('concept_summary')}")

    # Step 2: Chain Analyzer
    if verbose:
        print("\n[2/5] 🔗 Chain Analyzer: decomposing industry chain...")
    state["chain"] = chain_analyzer.analyze(concept_name, state["plan"])
    nodes = state["chain"]["chain_nodes"]
    if verbose:
        print(f"    Got {len(nodes)} nodes: {[n['name'] for n in nodes]}")

    # Step 3: Node Expander (parallel across nodes)
    if verbose:
        print(f"\n[3/5] 🔍 Node Expander: picking stocks for {len(nodes)} nodes in parallel...")
    candidate_pool = node_expander.build_candidate_pool(state["concept_code"])
    if verbose:
        print(f"    Candidate pool: {len(candidate_pool)} stocks from concept board")

    if not candidate_pool:
        raise RuntimeError(
            f"Concept {state['concept_code']} has empty stock list. "
            "Tushare concept_detail may need a different concept source."
        )

    state["node_picks"] = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(node_expander.expand, concept_name, n, candidate_pool): n["name"]
            for n in nodes
        }
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                state["node_picks"][name] = fut.result()
                if verbose:
                    n_picks = len(state["node_picks"][name].get("picks", []))
                    print(f"    ✓ {name}: {n_picks} picks")
            except Exception as e:
                print(f"    ✗ {name}: FAILED ({e})")
                state["node_picks"][name] = {"picks": [], "error": str(e)}

    # Step 4: Evidence Reviewer
    if verbose:
        print("\n[4/5] 🔎 Evidence Reviewer: checking consistency...")
    state["review"] = evidence_reviewer.review(concept_name, state["chain"], state["node_picks"])
    if verbose:
        print(f"    Logic score: {state['review'].get('logic_score')}/10")
        print(f"    Conflicts: {state['review'].get('conflicts')}")

    # Step 5: Portfolio Builder
    if verbose:
        print("\n[5/5] 📊 Portfolio Builder: assembling final portfolio...")
    state["portfolio"] = portfolio_builder.build(state["node_picks"], state["review"])
    if verbose:
        print(f"    Final portfolio: {state['portfolio']['size']} stocks")

    # Save run artifact
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = concept_name.replace("/", "_")
    out_path = OUTPUT_DIR / f"{safe_name}_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    if verbose:
        print(f"\n💾 Saved to {out_path}")

    return state

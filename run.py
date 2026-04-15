"""Entry point: run concept pipeline + backtest.

Usage:
    python run.py "AI算力"
    python run.py "AI算力" --backtest-start 20250101 --backtest-end 20260414
"""
import argparse
import sys

from graph import run_concept_pipeline
from backtest import backtest_equal_weight, print_backtest_report


def main():
    parser = argparse.ArgumentParser(description="Concept stock selection via multi-agent LLM pipeline")
    parser.add_argument("concept", help="Concept name (e.g., 'AI算力')")
    parser.add_argument("--concept-code", help="Tushare concept code (optional; auto-matched if omitted)")
    parser.add_argument("--skip-backtest", action="store_true", help="Skip backtest step")
    parser.add_argument("--backtest-start", default="20250101", help="Backtest start YYYYMMDD")
    parser.add_argument("--backtest-end", default="20260414", help="Backtest end YYYYMMDD")
    args = parser.parse_args()

    print(f"\n🚀 Running concept pipeline: {args.concept}\n" + "=" * 50)
    state = run_concept_pipeline(args.concept, concept_code=args.concept_code)

    print("\n📋 Final Portfolio:")
    for i, p in enumerate(state["portfolio"]["portfolio"], 1):
        buckets = "/".join(set(p["buckets"]))
        print(f"  {i:2d}. {p['ts_code']} {p['name']:10s} [{buckets}] score={p['score']} nodes={p['nodes']}")

    if args.skip_backtest:
        return

    print("\n🏁 Running backtest...")
    try:
        ts_codes = [p["ts_code"] for p in state["portfolio"]["portfolio"]]
        result = backtest_equal_weight(ts_codes, args.backtest_start, args.backtest_end)
        print_backtest_report(result)
    except Exception as e:
        print(f"⚠️  Backtest failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

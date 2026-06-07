import argparse
import asyncio
import json
import sys

from backend.scheduler.jobs import evaluate_user
from backend.selftest.scenario_runner import run_all_scenarios


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kairos", description="Kairos CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    evaluate = sub.add_parser("evaluate", help="Evaluate suggestions for a user")
    evaluate.add_argument("--user", required=True, help="User fixture key (mo, anneka, darian)")
    evaluate.add_argument("--mock", action="store_true", help="Use mock providers and message gen")
    evaluate.add_argument("--scenario", help="Optional scenario fixture override")
    evaluate.add_argument("--json", action="store_true", help="Output JSON")

    selftest = sub.add_parser("selftest", help="Run YAML self-test scenarios")
    selftest.add_argument("--json", action="store_true", help="Output JSON")

    return parser


async def cmd_evaluate(args: argparse.Namespace) -> int:
    result = await evaluate_user(args.user, mock=args.mock, scenario=args.scenario)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"User: {result['user']}  scenario: {result.get('scenario')}")
        print(f"Candidates scored: {result['candidates_count']}")
        for s in result["suggestions"]:
            print(
                f"  [{s['hobby_type']}] score={s['score']:.2f} "
                f"{s['window_start']} — {s['conditions']}"
            )
            print(f"    {s['message']}")
    return 0


async def cmd_selftest(args: argparse.Namespace) -> int:
    results = await run_all_scenarios()
    passed = sum(1 for r in results if r.passed)
    if args.json:
        print(
            json.dumps(
                [{"id": r.scenario_id, "passed": r.passed, "message": r.message} for r in results],
                indent=2,
            )
        )
    else:
        for r in results:
            status = "PASS" if r.passed else "FAIL"
            print(f"{status} {r.scenario_id}: {r.message}")
        print(f"\n{passed}/{len(results)} scenarios passed")
    return 0 if passed == len(results) else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "evaluate":
        return asyncio.run(cmd_evaluate(args))
    if args.command == "selftest":
        return asyncio.run(cmd_selftest(args))
    return 1


if __name__ == "__main__":
    sys.exit(main())

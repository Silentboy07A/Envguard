import argparse
import json
import sys

from .env import Env
from .resolver import Resolver
from .analyzer import Analyzer
from .scanner import SecretScanner
from .git import GitIntegration


def cmd_scan(args):
    env = Env(args.file)

    Resolver(env).resolve_all()

    scanner = SecretScanner(env)
    findings = scanner.scan()

    if not findings:
        print("✓ No secrets found.")
        return

    print("Secrets Found")
    print("-" * 40)

    for finding in findings:
        print(
            f"[{finding['severity']}] "
            f"{finding['type']} "
            f"({finding['key']}) "
            f"{finding['value']}"
        )


def cmd_analyze(args):
    env = Env(args.file)

    analyzer = Analyzer(env)

    print("Duplicates :", analyzer.find_duplicates())
    print("Empty      :", analyzer.find_empty_values())

    if args.required:
        print(
            "Missing   :",
            analyzer.find_missing(args.required),
        )


def cmd_compare(args):
    env = Env(args.file)
    example = Env(args.example)

    analyzer = Analyzer(env)

    result = analyzer.compare(example)

    print(json.dumps(result, indent=2))


def cmd_git_status(args):
    git = GitIntegration()

    status = git.status()

    print(json.dumps(status, indent=2))


def cmd_explain(args):
    env = Env(args.file)

    print(json.dumps(env.explain(args.key), indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="envguard",
        description="Static analysis and configuration intelligence for .env files.",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    scan = subparsers.add_parser("scan")
    scan.add_argument("-f", "--file", default=".env")
    scan.set_defaults(func=cmd_scan)

    analyze = subparsers.add_parser("analyze")
    analyze.add_argument("-f", "--file", default=".env")
    analyze.add_argument(
        "--required",
        nargs="*",
        default=[],
    )
    analyze.set_defaults(func=cmd_analyze)

    compare = subparsers.add_parser("compare")
    compare.add_argument("-f", "--file", default=".env")
    compare.add_argument("example")
    compare.set_defaults(func=cmd_compare)

    git = subparsers.add_parser("git-status")
    git.set_defaults(func=cmd_git_status)

    explain = subparsers.add_parser("explain")
    explain.add_argument("key")
    explain.add_argument("-f", "--file", default=".env")
    explain.set_defaults(func=cmd_explain)

    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
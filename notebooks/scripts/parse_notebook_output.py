#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def _load_json(path: str | None) -> dict:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return json.load(sys.stdin)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse Databricks jobs get-run-output JSON and print notebook exit payload."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to get-run-output JSON file. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the parsed notebook payload as formatted JSON.",
    )
    args = parser.parse_args()

    try:
        root = _load_json(args.input)
        notebook_output = root.get("notebook_output") or {}
        result = notebook_output.get("result")
        if not result:
            print("No notebook_output.result found.", file=sys.stderr)
            return 2

        payload = json.loads(result) if isinstance(result, str) else result
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to parse run output: {exc}", file=sys.stderr)
        return 1

    if args.pretty:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"ok={payload.get('ok')}")
    print(f"table={payload.get('table')}")
    print(f"message={payload.get('message')}")
    previews = payload.get("previews") or {}
    print(f"previews_count={len(previews)}")
    if payload.get("preview"):
        print(f"preview_source_cell={payload['preview'].get('source_cell')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

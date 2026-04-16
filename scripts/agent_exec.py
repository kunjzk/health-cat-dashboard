#!/usr/bin/env python3
"""
Iterative command execution on a Databricks all-purpose cluster.

Use this as an AI-agent loop primitive:
- create execution context
- run one or more Python commands while preserving state
- print results locally
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import compute


def _read_commands(command: str | None, command_file: str | None) -> list[str]:
    if command and command_file:
        raise ValueError("Use either --command or --command-file, not both.")
    if command:
        return [command]
    if command_file:
        with open(command_file, "r", encoding="utf-8") as f:
            contents = f.read().strip()
        if not contents:
            raise ValueError("Command file is empty.")
        return [contents]
    data = sys.stdin.read().strip()
    if data:
        return [data]
    raise ValueError("Provide --command, --command-file, or pipe command text via stdin.")


def _print_result(idx: int, result: compute.Results) -> None:
    result_type = result.result_type.value if result.result_type else "UNKNOWN"
    print(f"\n--- Result #{idx} ({result_type}) ---")
    if result.data:
        print(result.data)
    if result.summary:
        print(f"Summary: {result.summary}")
    if result.cause:
        print(f"Cause: {result.cause}")


def run_commands(cluster_id: str, commands: Iterable[str]) -> int:
    w = WorkspaceClient(profile=os.getenv("DATABRICKS_PROFILE", "kk-dev"))
    ctx = w.command_execution.create(
        cluster_id=cluster_id,
        language=compute.Language.PYTHON,
    ).result()
    context_id = ctx.id
    print(f"Created context: {context_id}")
    try:
        for idx, cmd in enumerate(commands, start=1):
            print(f"\n>>> Executing command #{idx}")
            exec_result = w.command_execution.execute(
                cluster_id=cluster_id,
                context_id=context_id,
                language=compute.Language.PYTHON,
                command=cmd,
            ).result()
            if exec_result.results is None:
                print("No results returned.")
                continue
            _print_result(idx, exec_result.results)
            if exec_result.results.result_type == compute.ResultType.ERROR:
                return 1
    finally:
        w.command_execution.destroy(cluster_id=cluster_id, context_id=context_id)
        print(f"\nDestroyed context: {context_id}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute Python on Databricks cluster context.")
    parser.add_argument("--cluster-id", default=os.getenv("DATABRICKS_CLUSTER_ID"), help="Databricks all-purpose cluster ID.")
    parser.add_argument("--command", help="Single Python command string to execute.")
    parser.add_argument("--command-file", help="Path to file containing Python command(s).")
    args = parser.parse_args()

    if not args.cluster_id:
        print("Missing cluster ID. Set --cluster-id or DATABRICKS_CLUSTER_ID.", file=sys.stderr)
        return 2

    try:
        commands = _read_commands(args.command, args.command_file)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    return run_commands(args.cluster_id, commands)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Submit a one-time notebook job run and print result details.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs


def wait_for_run(w: WorkspaceClient, run_id: int, poll_seconds: int) -> jobs.Run:
    while True:
        run = w.jobs.get_run(run_id=run_id)
        state = run.state
        lifecycle = state.life_cycle_state.value if state and state.life_cycle_state else "UNKNOWN"
        result = state.result_state.value if state and state.result_state else "UNKNOWN"
        print(f"Run {run_id}: life_cycle_state={lifecycle}, result_state={result}")
        if lifecycle in {"TERMINATED", "SKIPPED", "INTERNAL_ERROR"}:
            return run
        time.sleep(poll_seconds)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Databricks notebook as one-time job.")
    parser.add_argument("--notebook-path", required=True, help="Workspace notebook path to run.")
    parser.add_argument("--cluster-id", help="Existing all-purpose cluster ID.")
    parser.add_argument("--poll-seconds", type=int, default=5, help="Polling interval in seconds.")
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        help="Notebook parameter in key=value form. Can be repeated.",
    )
    args = parser.parse_args()

    profile = os.getenv("DATABRICKS_PROFILE", "kk-dev")
    cluster_id = args.cluster_id or os.getenv("DATABRICKS_CLUSTER_ID")
    if not cluster_id:
        print("Missing cluster ID. Provide --cluster-id or set DATABRICKS_CLUSTER_ID.", file=sys.stderr)
        return 2

    base_parameters: dict[str, str] = {}
    for raw in args.param:
        if "=" not in raw:
            print(f"Invalid --param value: {raw}. Expected key=value.", file=sys.stderr)
            return 2
        key, value = raw.split("=", 1)
        base_parameters[key] = value

    w = WorkspaceClient(profile=profile)

    submit = w.jobs.submit(
        run_name=f"ad-hoc-notebook-run:{args.notebook_path}",
        tasks=[
            jobs.SubmitTask(
                task_key="notebook_task",
                existing_cluster_id=cluster_id,
                notebook_task=jobs.NotebookTask(
                    notebook_path=args.notebook_path,
                    base_parameters=base_parameters if base_parameters else None,
                ),
            )
        ],
    )
    run_id = submit.response.run_id
    if run_id is None:
        print("Failed to receive run_id from submit response.", file=sys.stderr)
        return 1
    print(f"Submitted run_id: {run_id}")

    run = wait_for_run(w, run_id=run_id, poll_seconds=args.poll_seconds)
    output = w.jobs.get_run_output(run_id=run_id)

    state = run.state
    lifecycle = state.life_cycle_state.value if state and state.life_cycle_state else "UNKNOWN"
    result = state.result_state.value if state and state.result_state else "UNKNOWN"
    print(f"\nFinal state: {lifecycle} / {result}")
    print(f"Run page: {run.run_page_url}")

    if output.notebook_output and output.notebook_output.result is not None:
        print("\nNotebook result (dbutils.notebook.exit):")
        print(output.notebook_output.result)
    elif output.error:
        print("\nRun error:")
        print(output.error)
    else:
        print("\nNo notebook exit result returned.")

    return 0 if result == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

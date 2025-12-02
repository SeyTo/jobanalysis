import os
from pathlib import Path

# from pync import Notifier


def notify_and_open_report(report_name: str):
    project_root = Path(__file__).resolve().parent.parent
    target = (project_root / "reports" / f"{report_name}.xlsx").resolve()

    if not target.exists():
        print(f"[notify] File not found: {target}")
        return
    # Optional: ensure it exists before notifying
    if not os.path.exists(target):
        print(f"[notify] File not found: {target}")
        return

    try:
        # TODO:
        # Notifier.notify(
        #     "Generated new job reports",
        #     title="Job Reports",
        #     sound="glass",
        #     open=f"file://{target}",  # <— opens in default app
        # )
        print(f"[notify] Sent notification for {target}")
    except Exception as e:
        # Make sure errors land in your launchd stderr log
        import sys
        import traceback

        traceback.print_exc(file=sys.stderr)

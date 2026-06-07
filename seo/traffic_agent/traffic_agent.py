"""Traffic agent CLI — drive discovery without social/Reddit."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .actions import run_instant_tier
from .email_tips import run_email_tips
from .post_generator import generate_all_drafts


def _init_tracker() -> None:
    if config.TRACKER_FILE.exists():
        return
    registry = config.load_registry()
    with open(config.TRACKER_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "tier", "status", "last_run_at", "notes"])
        for p in sorted(registry["platforms"], key=lambda x: x.get("priority", 99)):
            w.writerow([p["id"], p["name"], p["tier"], "pending", "", ""])


def _update_tracker(platform_id: str, status: str, note: str = "") -> None:
    if not config.TRACKER_FILE.exists():
        _init_tracker()
    rows = []
    with open(config.TRACKER_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    now = datetime.now(timezone.utc).isoformat()
    for row in rows:
        if row["id"] == platform_id:
            row["status"] = status
            row["last_run_at"] = now
            if note:
                row["notes"] = note[:200]
    with open(config.TRACKER_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "name", "tier", "status", "last_run_at", "notes"])
        w.writeheader()
        w.writerows(rows)


def cmd_map(args: argparse.Namespace) -> None:
    registry = config.load_registry()
    tiers = registry["tiers"]
    by_tier: dict[str, list] = {}
    for p in registry["platforms"]:
        by_tier.setdefault(p["tier"], []).append(p)

    print("=== Traffic Platform Map (Hobie Cunningham / OWL AI Agency) ===\n")
    order = ["instant", "env_credentials", "email_no_account", "draft_only", "manual_account"]
    for tier in order:
        print(f"## {tier.upper()} — {tiers.get(tier, '')}")
        for p in sorted(by_tier.get(tier, []), key=lambda x: x.get("priority", 99)):
            print(f"  [{p['id']}] {p['name']} (action: {p.get('action')})")
        print()


def cmd_run_auto(args: argparse.Namespace) -> None:
    _init_tracker()
    config.ensure_dirs()
    print("=== Tier INSTANT (no account) ===")
    for item in run_instant_tier():
        print(json.dumps(item))
        action = item.get("action", "unknown")
        status = "done" if not item.get("error") and not item.get("skipped") else "skipped"
        _update_tracker(action, status, json.dumps(item)[:100])

    if not args.skip_email:
        print("\n=== Tier EMAIL (no portal account) ===")
        for item in run_email_tips(dry_run=args.dry_run, delay=args.email_delay):
            print(json.dumps(item))
            pid = item.get("platform_id", "email")
            if item.get("ok"):
                _update_tracker(pid, "sent")
            elif item.get("dry_run"):
                _update_tracker(pid, "dry_run")
            else:
                _update_tracker(pid, "error", item.get("error", ""))

    print("\n=== Tier DRAFT + FORM PAYLOADS ===")
    paths = generate_all_drafts()
    for path in paths:
        print(f"Wrote {path}")
    registry = config.load_registry()
    for p in registry["platforms"]:
        if p.get("action") in ("generate_post", "form_payload"):
            _update_tracker(p["id"], "draft_ready", str(config.DRAFTS_DIR))


def cmd_status(args: argparse.Namespace) -> None:
    _init_tracker()
    with open(config.TRACKER_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            print(f"{row['tier']:18} {row['status']:12} {row['id']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="OWL Traffic Agent")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("map", help="Show platforms by automation tier")

    run_p = sub.add_parser("run-auto", help="Run instant + email tips + generate drafts")
    run_p.add_argument("--dry-run", action="store_true", help="Skip Zoho sends")
    run_p.add_argument("--skip-email", action="store_true", help="Skip tip emails")
    run_p.add_argument("--email-delay", type=int, default=120)

    sub.add_parser("status", help="Tracker status")
    sub.add_parser("drafts", help="Regenerate post drafts and form payloads only")

    args = parser.parse_args()
    if args.cmd == "map":
        cmd_map(args)
    elif args.cmd == "run-auto":
        cmd_run_auto(args)
    elif args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "drafts":
        config.ensure_dirs()
        for path in generate_all_drafts():
            print(path)


if __name__ == "__main__":
    main()

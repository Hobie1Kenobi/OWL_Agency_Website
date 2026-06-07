"""CLI entry for GEO + Nurture agent."""

from __future__ import annotations

import argparse

from . import config
from .geo_agent import run_geo_command
from .nurture_agent import run_nurture_command


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OWL GEO + Nurture Agent — generative engine optimization and lead email sequences"
    )
    sub = parser.add_subparsers(dest="domain", required=True)

    geo = sub.add_parser("geo", help="GEO tasks: llms.txt, robots, audits, indexing")
    geo_sub = geo.add_subparsers(dest="command", required=True)
    geo_sub.add_parser("llms", help="Generate llms.txt at site root")
    geo_sub.add_parser("robots-audit", help="Audit robots.txt for AI crawlers")
    geo_sub.add_parser("robots-patch", help="Add explicit AI crawler Allow rules")
    geo_sub.add_parser("audit", help="Full GEO audit report")
    idx = geo_sub.add_parser("indexing", help="Daily GSC indexing plan (+ IndexNow if configured)")
    idx.add_argument("--day", type=int, default=0, help="Day offset for URL rotation")

    nurture = sub.add_parser("nurture", help="Resend nurture sequences for intake leads")
    nurture_sub = nurture.add_subparsers(dest="command", required=True)
    nurture_sub.add_parser("queue", help="Show intakes due for nurture emails")
    prev = nurture_sub.add_parser("preview", help="Preview email for a stage")
    prev.add_argument("--stage", type=int, default=0)
    run_p = nurture_sub.add_parser("run", help="Send due nurture emails")
    run_p.add_argument("--confirm", action="store_true", help="Actually send (default is dry-run)")
    run_p.add_argument("--dry-run", action="store_true", help="Force dry-run even with --confirm")

    setup = sub.add_parser("setup", help="Run initial GEO setup (llms + robots patch + audit)")

    args = parser.parse_args()
    config.ensure_dirs()

    if args.domain == "geo":
        run_geo_command(args.command, day=getattr(args, "day", 0))
    elif args.domain == "nurture":
        dry_run = not getattr(args, "confirm", False) or getattr(args, "dry_run", False)
        if args.command == "preview":
            run_nurture_command("preview", stage=args.stage)
        elif args.command == "run":
            run_nurture_command("run", dry_run=dry_run, confirm=getattr(args, "confirm", False))
        else:
            run_nurture_command(args.command)
    elif args.domain == "setup":
        run_geo_command("llms")
        run_geo_command("robots-patch")
        run_geo_command("audit")
        print("\nSetup complete. Deploy llms.txt and robots.txt to production.")
        print("Schedule nurture: python run_geo_nurture.py nurture run --confirm")


if __name__ == "__main__":
    main()

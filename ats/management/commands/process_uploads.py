from __future__ import annotations

from pathlib import Path
from datetime import datetime
import shutil
import re

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = (
        "Scan `uploads/` for files and move matching fake CVs into jobs/<id>/ folders."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Don't move files, only report what would be done.",
        )

    def handle(self, *args, **options):
        base_dir = Path(getattr(settings, "BASE_DIR", Path(__file__).resolve().parents[3]))
        uploads_dir = base_dir / "uploads"
        jobs_dir = base_dir / "jobs"

        if not uploads_dir.exists() or not jobs_dir.exists():
            if not uploads_dir.exists():
                self.stdout.write(self.style.WARNING(f"Uploads dir not found: {uploads_dir}"))
            if not jobs_dir.exists():
                self.stdout.write(self.style.WARNING(f"Jobs dir not found: {jobs_dir}"))
            return

        processed = 0
        dry = options.get("dry_run", False)
        def extract_tokens(s: str) -> list:
            """Return a list of lowercase word-like tokens from the input string.

            This uses a Unicode-aware regex to capture accented letters and digits,
            which helps match Hungarian words like 'fejlesztő'.
            """
            if not s:
                return []
            s = s.lower()
            # Map c++ -> cpp
            s = s.replace("c++", " cpp ")
            toks = re.findall(r"[a-z0-9\u00e0-\u024f]+", s, flags=re.IGNORECASE)
            return [t.strip() for t in toks if t.strip()]

        def build_token_map() -> dict:
            """Scan `jobs/` filenames and build token -> set(job_id) map."""
            token_map: dict[str, set[str]] = {}
            for jf in jobs_dir.glob("[0-9]*-*.md"):
                stem = jf.stem
                # remove leading id and dash
                rest = re.sub(r"^[0-9]+-", "", stem)
                # normalize like filenames
                for tok in extract_tokens(rest):
                    token_map.setdefault(tok, set()).add(jf.stem.split("-")[0].strip("[]"))
            return token_map

        # Additional token classification
        GENERIC_TOKENS = {"developer", "sap", "fejleszt", "programoz", "automat"}

        # Build map from existing jobs
        token_map = build_token_map()

        def analyze_name(name: str) -> dict:
            """Return analysis dict with:
            - mapped_ids: all job ids matched by any token
            - specific_ids: ids matched by non-generic tokens
            - generic: whether a generic token
                - (developer, sap, fejlesztő, fejleszto, programozó, programozo)
            - is present
            """
            # analyze filename (without extension) and extract tokens
            stem = re.sub(r"\.[^.]+$", "", name)
            tokens = set(extract_tokens(stem))
            mapped_ids = set()
            specific_ids = set()
            # Match tokens against token_map keys using exact or substring matches.
            # This handles joined words like 'szoftverfejleszto' matching 'fejleszto'.
            for tok in tokens:
                for key, ids in token_map.items():
                    if key == tok or key in tok or tok in key:
                        mapped_ids.update(ids)
                        if key not in GENERIC_TOKENS:
                            specific_ids.update(ids)

            # Generic present if any generic token matches by substring as well
            generic_present = False
            for tok in tokens:
                for gen in GENERIC_TOKENS:
                    if gen == tok or gen in tok or tok in gen:
                        generic_present = True
                        break
                if generic_present:
                    break
            return {
                "mapped_ids": mapped_ids,
                "specific_ids": specific_ids,
                "generic": generic_present,
            }

        def ensure_and_move(item_path: Path, target_dir: Path, dry_run: bool) -> bool:
            if not target_dir.exists():
                if dry_run:
                    self.stdout.write(f"Would create directory: {target_dir}")
                else:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    self.stdout.write(f"Created directory: {target_dir}")

            stem = item_path.stem
            suffix = item_path.suffix
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            new_name = f"{stem}_{ts}{suffix}"
            dest = target_dir / new_name

            if dry_run:
                self.stdout.write(f"Would move {item_path} -> {dest}")
                return False
            shutil.move(str(item_path), str(dest))
            self.stdout.write(self.style.SUCCESS(f"Moved {item_path.name} -> {dest}"))
            return True

        for item in sorted(uploads_dir.iterdir()):
            if not item.is_file():
                continue
            # Skip repository metadata files like .gitkeep
            if item.name == ".gitkeep":
                continue
            name = item.name
            # First check extension: image formats are rejected (go to jobs/0)
            image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.tif', '.tiff', '.bmp', '.webp'}
            suffix = item.suffix.lower()
            if suffix in image_exts:
                # route images to rejected bucket '0'
                target = jobs_dir / "0"
                if ensure_and_move(item, target, dry):
                    processed += 1
                continue

            analysis = analyze_name(name)
            mapped = analysis["mapped_ids"]
            specific = analysis["specific_ids"]
            generic = analysis["generic"]

            # Routing priority:
            # 1) If there are specific (non-generic) token matches -> prefer them
            # 2) If multiple specific ids -> ambiguous -> 00
            # 3) If exactly one specific id -> route there
            # 4) If no specific but generic token present -> 00
            # 5) If no specific and no generic but some mapped ids (unlikely) -> if single -> route, else -> 00
            # 6) Otherwise -> 0
            if specific:
                if len(specific) == 1:
                    jid = next(iter(specific))
                    target = jobs_dir / jid
                    if ensure_and_move(item, target, dry):
                        processed += 1
                    continue
                else:
                    self.stdout.write(self.style.WARNING(f"Ambiguous specific matches for {name}: {', '.join(sorted(specific))} -- sending to 00"))
                    target = jobs_dir / "00"
                    if ensure_and_move(item, target, dry):
                        processed += 1
                    continue

            if generic:
                self.stdout.write(self.style.WARNING(f"Generic token present for {name} -- sending to 00"))
                target = jobs_dir / "00"
                if ensure_and_move(item, target, dry):
                    processed += 1
                continue

            if mapped:
                if len(mapped) == 1:
                    jid = next(iter(mapped))
                    target = jobs_dir / jid
                    if ensure_and_move(item, target, dry):
                        processed += 1
                    continue
                else:
                    self.stdout.write(self.style.WARNING(f"Ambiguous matches for {name}: {', '.join(sorted(mapped))} -- sending to 00"))
                    target = jobs_dir / "00"
                    if ensure_and_move(item, target, dry):
                        processed += 1
                    continue

            # fallback: no matches
            target = jobs_dir / "0"
            if ensure_and_move(item, target, dry):
                processed += 1

        self.stdout.write(self.style.NOTICE(f"Processed files: {processed}"))

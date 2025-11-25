"""Management command to extract text from PDFs in the `jobs/` directory.

Usage:
  python manage.py scan_pdfs [--jobs-dir PATH] [--dry-run] [--force]

For each `*.pdf` found under `jobs/`, this command will create a sibling
`<name>.pdf.txt` (or `<name>.txt`) containing extracted text using
`ats.utils.text_extract.extract_text_from_file`.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from pathlib import Path
from ats.utils.text_extract import extract_text_from_file


class Command(BaseCommand):
    help = "Extract text from PDFs under the jobs directory and write .txt files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--jobs-dir",
            dest="jobs_dir",
            default=os.path.join(getattr(settings, 'BASE_DIR', '.'), 'jobs'),
            help="Path to the jobs directory (default: <BASE_DIR>/jobs)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Show what would be done without writing files",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            dest="force",
            help="Overwrite existing .txt files",
        )

    def handle(self, *args, **options):
        jobs_dir = Path(options['jobs_dir'])
        dry_run = options['dry_run']
        force = options['force']

        if not jobs_dir.exists():
            self.stderr.write(f"Jobs directory not found: {jobs_dir}")
            return

        pdf_count = 0
        written = 0
        skipped = 0

        for root, _dirs, files in os.walk(jobs_dir):
            for fname in files:
                if not fname.lower().endswith('.pdf'):
                    continue
                pdf_count += 1
                pdf_path = Path(root) / fname
                # prefer .txt with same base name
                out_path = pdf_path.with_suffix('.txt')

                if out_path.exists() and not force:
                    skipped += 1
                    self.stdout.write(f"Skipping (exists): {out_path}")
                    continue

                self.stdout.write(f"Processing: {pdf_path}")
                try:
                    text = extract_text_from_file(str(pdf_path))
                except ImportError as e:
                    self.stderr.write(str(e))
                    self.stderr.write("Install pdfminer.six to enable PDF extraction")
                    return

                if dry_run:
                    self.stdout.write(f"[dry-run] would write: {out_path} (len={len(text)})")
                    continue

                try:
                    with open(out_path, 'w', encoding='utf-8') as fh:
                        fh.write(text)
                    written += 1
                    self.stdout.write(f"Wrote: {out_path}")
                except Exception as e:
                    self.stderr.write(f"Failed to write {out_path}: {e}")

        self.stdout.write(f"Done. PDFs found: {pdf_count}. Written: {written}. Skipped: {skipped}.")

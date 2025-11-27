import os
import sys
import tempfile
from pathlib import Path

import django
from django.test import SimpleTestCase, override_settings
from django.core.management import call_command

# Ensure project root is on sys.path so Django settings package can be imported
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

# Ensure Django settings are configured for tests run via pytest
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ApplicantTrackingSystem.settings")
django.setup()



class ProcessUploadsCommandTests(SimpleTestCase):
    def test_moves_python_and_quality_and_ambiguous_to_00(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            uploads = base / "uploads"
            jobs = base / "jobs"
            uploads.mkdir()
            jobs.mkdir()

            # create job markers (not used directly by matching but present)
            (jobs / "16-python.md").write_text("# python job")
            (jobs / "15-cpp.md").write_text("# cpp job")
            (jobs / "27-quality.md").write_text("# quality job")
            # add sap/abap job and leave java absent to test 0 vs 00 behavior
            (jobs / "1-sap-abap.md").write_text("# sap abap job")

            # uploads
            (uploads / "alice_python_cv.pdf").write_bytes(b"pdf")
            (uploads / "bob_quality_resume.pdf").write_bytes(b"pdf")
            (uploads / "charlie_python_cpp.docx").write_bytes(b"doc")

            with override_settings(BASE_DIR=str(base)):
                call_command("process_uploads")

            # python -> jobs/16
            files_16 = list((jobs / "16").glob("*") if (jobs / "16").exists() else [])
            self.assertTrue(any("alice_python_cv" in p.name for p in files_16))

            # quality -> jobs/27
            files_27 = list((jobs / "27").glob("*") if (jobs / "27").exists() else [])
            self.assertTrue(any("bob_quality_resume" in p.name for p in files_27))

            # ambiguous (python+cpp) -> jobs/00
            files_00 = list((jobs / "00").glob("*") if (jobs / "00").exists() else [])
            self.assertTrue(any("charlie_python_cpp" in p.name for p in files_00))
            # java developer - no java job exists => goes to 00 because developer is generic
            (uploads / "daniel_java_developer.pdf").write_bytes(b"pdf")
            # sap abap -> specific job 1
            (uploads / "eva_sap_abap.pdf").write_bytes(b"pdf")

            with override_settings(BASE_DIR=str(base)):
                call_command("process_uploads")

            files_00 = list((jobs / "00").glob("*") if (jobs / "00").exists() else [])
            self.assertTrue(any("daniel_java_developer" in p.name for p in files_00))
            files_1 = list((jobs / "1").glob("*") if (jobs / "1").exists() else [])
            self.assertTrue(any("eva_sap_abap" in p.name for p in files_1))

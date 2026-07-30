import sys, unittest
from datetime import datetime, timezone
sys.path.insert(0, "scripts")
from artifact_naming import artifact_path, validate_relative_path, run_id_from_datetime
class NamingTests(unittest.TestCase):
 def test_fixed_slug_and_utc_path(self):
  instant=datetime(2026,7,30,15,50,29,637000,tzinfo=timezone.utc)
  self.assertEqual(run_id_from_datetime(instant),"20260730T155029-637")
  self.assertEqual(artifact_path("engineer","implementation-report",instant),"artifacts/engineer/20260730T155029-637__implementation-report.md")
 def test_rejects_legacy_and_escape(self):
  for path in ("artifacts/spec.md","../x","artifacts/engineer/latest.md","artifacts" + chr(92) + "engineer" + chr(92) + "x.md"):
   self.assertFalse(validate_relative_path(path))

import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,"scripts")
from artifact_io import create_new_utf8, sha256_file
class IoTests(unittest.TestCase):
 def test_exclusive_write_preserves_existing_bytes(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"x.md"; create_new_utf8(p,"one"); before=sha256_file(p)
   with self.assertRaises(FileExistsError): create_new_utf8(p,"two")
   self.assertEqual(before,sha256_file(p))

import json, subprocess, sys, tempfile, unittest
from pathlib import Path

SRC = {"requirements": [
    {"chapter_id": "V6", "chapter_name": "Authentication", "section_id": "V6.2",
     "section_name": "Password Security", "req_id": "V6.2.1", "req_description": "Verify eight.", "L": "1"},
    {"chapter_id": "V6", "chapter_name": "Authentication", "section_id": "V6.2",
     "section_name": "Password Security", "req_id": "V6.2.9", "req_description": "Verify sixty-four.", "L": "2"},
    {"chapter_id": "V1", "chapter_name": "Encoding", "section_id": "V1.2",
     "section_name": "Injection", "req_id": "V1.2.4", "req_description": "Verify params.", "L": "1"},
    {"chapter_id": "V6", "chapter_name": "Authentication", "section_id": "V6.3",
     "section_name": "General", "req_id": "V6.3.3", "req_description": "Verify MFA.", "L": "3"},
]}

class ExtractTests(unittest.TestCase):
    def run_tool(self, selection):
        d = Path(tempfile.mkdtemp())
        (d / "src.json").write_text(json.dumps(SRC))
        (d / "sel.txt").write_text(selection)
        p = subprocess.run([sys.executable, "dev/extract_asvs.py", d / "src.json", d / "sel.txt", d / "out.json"],
                           capture_output=True, text=True)
        return p, d / "out.json"

    def test_extracts_selected_sorted_by_number(self):
        p, out = self.run_tool("# core\nV6.2.9\nV6.2.1\nV1.2.4\n")
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(out.read_text())
        self.assertEqual([r["id"] for r in data], ["V1.2.4", "V6.2.1", "V6.2.9"])
        self.assertEqual(data[1], {"id": "V6.2.1", "level": 1, "chapter_id": "V6", "chapter_name": "Authentication",
                                   "section_id": "V6.2", "section_name": "Password Security", "text": "Verify eight."})

    def test_missing_id_fails_and_names_it(self):
        p, _ = self.run_tool("V6.2.1\nV9.9.9\n")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("V9.9.9", p.stderr)

    def test_level3_id_fails_and_names_it(self):
        p, _ = self.run_tool("V6.3.3\n")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("V6.3.3", p.stderr)

if __name__ == "__main__":
    unittest.main()

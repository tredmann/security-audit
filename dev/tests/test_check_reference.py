import json, subprocess, sys, tempfile, unittest
from pathlib import Path

SEL = [{"id": "V6.2.1", "level": 1, "chapter_id": "V6", "chapter_name": "Authentication",
        "section_id": "V6.2", "section_name": "Password Security", "text": "Verify eight."}]
GOOD = """### V6.2.1 (Level 1, core, own-auth)
**Requirement:** Verify eight.
**Where to look:** registration validation.
**Implemented when:** min length >= 8.
**Not implemented when:** no rule.
"""

class CheckReferenceTests(unittest.TestCase):
    def run_tool(self, md):
        d = Path(tempfile.mkdtemp())
        (d / "ref.md").write_text(md); (d / "sel.json").write_text(json.dumps(SEL))
        return subprocess.run([sys.executable, "dev/check_reference.py", d / "ref.md", d / "sel.json"],
                              capture_output=True, text=True)

    def test_good_file_passes(self):
        self.assertEqual(self.run_tool(GOOD).returncode, 0)

    def test_reworded_requirement_fails(self):
        p = self.run_tool(GOOD.replace("Verify eight.", "Verify 8."))
        self.assertEqual(p.returncode, 1); self.assertIn("V6.2.1", p.stdout)

    def test_missing_field_fails(self):
        p = self.run_tool(GOOD.replace("**Not implemented when:** no rule.\n", ""))
        self.assertEqual(p.returncode, 1); self.assertIn("Not implemented when", p.stdout)

    def test_missing_id_fails(self):
        p = self.run_tool("# nothing\n")
        self.assertEqual(p.returncode, 1); self.assertIn("V6.2.1", p.stdout)

    def test_unknown_id_fails(self):
        p = self.run_tool(GOOD + GOOD.replace("V6.2.1", "V9.9.9"))
        self.assertEqual(p.returncode, 1); self.assertIn("V9.9.9", p.stdout)

    def test_bad_condition_key_fails(self):
        p = self.run_tool(GOOD.replace("own-auth", "login"))
        self.assertEqual(p.returncode, 1); self.assertIn("login", p.stdout)

    def test_new_condition_keys_pass(self):
        for key in ("dockerfile", "compose", "ci"):
            p = self.run_tool(GOOD.replace("core, own-auth", "conditional: " + key))
            self.assertEqual(p.returncode, 0, key)

    def test_empty_field_body_fails(self):
        p = self.run_tool(GOOD.replace("**Where to look:** registration validation.", "**Where to look:**"))
        self.assertEqual(p.returncode, 1); self.assertIn("field: V6.2.1 Where to look", p.stdout)

    def test_level_mismatch_fails(self):
        p = self.run_tool(GOOD.replace("Level 1", "Level 2"))
        self.assertEqual(p.returncode, 1); self.assertIn("level: V6.2.1 Level 2 Level 1", p.stdout)

    def test_duplicate_id_fails(self):
        p = self.run_tool(GOOD + GOOD)
        self.assertEqual(p.returncode, 1); self.assertIn("duplicate: V6.2.1", p.stdout)

if __name__ == "__main__":
    unittest.main()

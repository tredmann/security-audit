import subprocess, unittest
from pathlib import Path

GREP = r"robust|state[- ]of[- ]the[- ]art|best[- ]in[- ]class|industry[- ]leading|cutting[- ]edge|top priority|highest priority|takes? security seriously|committed to|world[- ]class|enterprise[- ]grade|military[- ]grade|bank[- ]level|not only|—|–"

class TemplateTests(unittest.TestCase):
    def test_templates_exist(self):
        for name in ["checklist.md", "TODO.md", "contact.md", "SECURITY.md"]:
            self.assertTrue(Path("templates", name).exists(), name)

    def test_templates_are_free_of_forbidden_words(self):
        p = subprocess.run(["grep", "-n", "-i", "-E", GREP] + [str(x) for x in Path("templates").glob("*.md")],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 1, p.stdout)

    def test_security_template_has_markers_and_disclaimer(self):
        t = Path("templates/SECURITY.md").read_text()
        self.assertLess(t.index("<!-- security-audit:start -->"), t.index("<!-- security-audit:end -->"))
        self.assertIn("It is not a penetration test", t)
        self.assertLess(t.index("<!-- security-audit:end -->"), t.index("## Further evidence"))

    def test_security_template_names_no_ids(self):
        t = Path("templates/SECURITY.md").read_text()
        self.assertNotIn("<ID>", t)
        self.assertNotIn("<AP-n>", t)
        self.assertIn("available to customers on request", t)

    def test_templates_quoting_asvs_carry_attribution(self):
        for name in ["checklist.md", "TODO.md", "SECURITY.md"]:
            self.assertIn("Requirement text from OWASP ASVS 5.0.0, CC BY-SA 4.0.", Path("templates", name).read_text(), name)

    def test_checklist_template_has_table_header_and_changes(self):
        t = Path("templates/checklist.md").read_text()
        self.assertIn("| ID | Level | Requirement | Status | Evidence | Reason | Checked |", t)
        self.assertIn("## Changes", t)

if __name__ == "__main__":
    unittest.main()

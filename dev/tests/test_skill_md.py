# dev/tests/test_skill_md.py
import re, unittest
from pathlib import Path

class SkillMdTests(unittest.TestCase):
    def setUp(self):
        self.text = Path("SKILL.md").read_text()
        m = re.match(r"^---\n(.*?)\n---\n", self.text, re.S)
        self.assertIsNotNone(m, "frontmatter missing"); self.fm = m.group(1)

    def test_frontmatter_name_and_description(self):
        self.assertIn("name: security-audit", self.fm)
        desc = re.search(r"^description: (.*)$", self.fm, re.M).group(1)
        self.assertTrue(desc.startswith("Use when"), desc)
        self.assertLess(len(self.fm), 1024)
        for kw in ["ASVS", "security checklist", "security audit", "self-assessment", "SECURITY.md"]:
            self.assertIn(kw, desc)

    def test_status_vocabulary_and_rules(self):
        for s in ["`implemented`", "`partial`", "`not implemented`", "`n/a`"]:
            self.assertIn(s, self.text)
        self.assertIn("security-audit:start", self.text)
        self.assertRegex(self.text, r"(?i)never write a secret value")

    def test_references_bundled_files(self):
        for f in ["reference/asvs-checks.md", "reference/additional-practices.md", "reference/detection.md",
                  "templates/checklist.md", "templates/TODO.md", "templates/contact.md", "templates/SECURITY.md"]:
            self.assertIn(f, self.text, f)

    def test_no_agent_specific_tool_names(self):
        for tool in ["Read tool", "Edit tool", "Bash tool", "Grep tool", "Glob tool", "TodoWrite"]:
            self.assertNotIn(tool, self.text, tool)

if __name__ == "__main__":
    unittest.main()

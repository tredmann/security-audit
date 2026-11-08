# dev/tests/test_consistency.py
import importlib.util, re, unittest
from pathlib import Path

def load_checker():
    spec = importlib.util.spec_from_file_location("check_reference", "dev/check_reference.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class ConsistencyTests(unittest.TestCase):
    def test_skill_md_body_word_limit(self):
        text = Path("SKILL.md").read_text()
        body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
        self.assertLessEqual(len(body.split()), 1200)

    def test_detection_keys_equal_checker_conditions(self):
        text = Path("reference/detection.md").read_text()
        conditions = text.split("## Conditions", 1)[1]
        keys = set(re.findall(r"^### (\S+)$", conditions, re.M))
        self.assertEqual(keys, load_checker().CONDITIONS)

    def test_additional_practices_have_four_fields(self):
        text = Path("reference/additional-practices.md").read_text()
        blocks = re.split(r"^### ", text, flags=re.M)[1:]
        self.assertEqual(len(blocks), 12)
        for block in blocks:
            for field in ["Reference", "Where to look", "Implemented when", "Not implemented when"]:
                m = re.search(r"^\*\*" + field + r":\*\*(.*)$", block, re.M)
                self.assertTrue(m and m.group(1).strip(), block.splitlines()[0] + " " + field)

if __name__ == "__main__":
    unittest.main()

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_levels


def lint(files):
    with tempfile.TemporaryDirectory() as root:
        for name, text in files.items():
            path = os.path.join(root, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
        return check_levels.lint_sources(root)


class LintTest(unittest.TestCase):
    def test_ungated_aise_command_in_shared_build(self):
        self.assertEqual(len(lint({'builds/x.pyai': 'use_build_vs(Protoss, Terran)\nwait_rand(0, 10)\n'})), 1)

    def test_gated_or_terran_only_is_ok(self):
        self.assertEqual(lint({
            'builds/x.pyai': 'use_build_vs(Protoss, Terran)\nif enemyowns(Command Center):\n    wait_rand(0, 10)\n',
            'builds/y.pyai': 'use_build_vs(Terran)\nwait_rand(0, 10)\n',
            'managers/z.pyai': 'loop()\n--aise_z--\nwait_rand(1, 2)\n',
        }), [])

    def test_aise_dir_text_rules(self):
        errors = lint({'aise/m.pyai': '# note: colon\nprint(a, b)\nbuild(1, Gas)\n'})
        self.assertEqual(len(errors), 3)


if __name__ == '__main__':
    unittest.main()

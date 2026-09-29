import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import levels

SRC = '''a()
if_level(2):
    b({lv.x})
    if_level(3):
        c()
d()'''


class LevelsTest(unittest.TestCase):
    def test_level_1_drops_blocks(self):
        self.assertEqual(levels.apply(SRC, {'level': 1}), 'a()\nd()')

    def test_level_2_keeps_outer_block_dedented(self):
        self.assertEqual(levels.apply(SRC, {'level': 2, 'x': 5}), 'a()\nb(5)\nd()')

    def test_level_3_keeps_nested_block(self):
        self.assertEqual(levels.apply(SRC, {'level': 3, 'x': 5}), 'a()\nb(5)\nc()\nd()')

    def test_nested_indented_code_keeps_relative_indent(self):
        src = 'if_level(1):\n    if owned(Gateway):\n        x()\ny()'
        self.assertEqual(levels.apply(src, {'level': 1}), 'if owned(Gateway):\n    x()\ny()')

    def test_missing_key_fails(self):
        with self.assertRaises(SystemExit) as cm:
            levels.apply('wait({lv.nope})', {'level': 1})
        self.assertIn('aise.nope', str(cm.exception))

    def test_key_in_dropped_block_not_required(self):
        self.assertEqual(levels.apply('if_level(3):\n    w({lv.nope})\nz()', {'level': 1}), 'z()')

    def test_markers_without_aise_config_fail(self):
        with self.assertRaises(SystemExit):
            levels.apply('if_level(1):\n    x()', None)

    def test_plain_source_untouched_without_config(self):
        self.assertEqual(levels.apply('build(1, Gateway)\n', None), 'build(1, Gateway)\n')

    def test_crlf_and_block_at_eof(self):
        self.assertEqual(levels.apply('a()\r\nif_level(2):\r\n    b()\r\n', {'level': 2}), 'a()\r\nb()\r\n')


if __name__ == '__main__':
    unittest.main()

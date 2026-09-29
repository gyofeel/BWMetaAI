import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pyms_compat

LEGACY = '''# comment before scripts
TMCx(1342, 101, aiscript):

--gen_main--
wait(1)
goto(gen_main)
--a-b--
goto(a-b)
build(1, Terran Command Center, 150)
# goto(gen_main) stays in comments
+Vi0(1520, 010, aiscript):
	--gen_main--
	goto(gen_main)
'''


class ConvertTest(unittest.TestCase):
    def setUp(self):
        self.out = pyms_compat.convert(LEGACY)

    def test_header_becomes_script_block(self):
        self.assertIn('script TMCx {\n    name_string 1342\n    bin_file aiscript\n'
                      '    broodwar_only 1\n    staredit_hidden 0\n    requires_location 1\n'
                      '    entry_point s0_entry\n}\n--s0_entry--', self.out)

    def test_flag_bits(self):
        self.assertIn('script +Vi0 {\n    name_string 1520\n    bin_file aiscript\n'
                      '    broodwar_only 0\n    staredit_hidden 1\n    requires_location 0\n', self.out)

    def test_labels_prefixed_per_script(self):
        self.assertIn('--s0_gen_main--\nwait(1)\ngoto(s0_gen_main)', self.out)
        self.assertIn('\t--s1_gen_main--\n\tgoto(s1_gen_main)', self.out)

    def test_hyphen_label_sanitized(self):
        self.assertIn('--s0_a_b--\ngoto(s0_a_b)', self.out)

    def test_plus_label_sanitized(self):
        out = pyms_compat.convert('TMCx(1342, 101, aiscript):\n--gen_+1_x--\nrandom_jump(2, gen_+1_x)\n')
        self.assertIn('--s0_gen__1_x--\nrandom_jump(2, s0_gen__1_x)', out)

    def test_digit_label_prefixed(self):
        out = pyms_compat.convert('TMCx(1342, 101, aiscript):\n--a--\ngoto(3_end)\n--3_end--\nwait(150)\n')
        self.assertIn('goto(s0_3_end)\n--s0_3_end--\nwait(150)', out)

    def test_dead_code_after_goto_gets_label(self):
        out = pyms_compat.convert('TMCx(1342, 101, aiscript):\n--a--\ngoto(a)\n\n# c\nwait(1)\nstop()\n--b--\nstop()\n')
        self.assertIn('goto(s0_a)\n\n# c\n--s0_dead_1--\nwait(1)\nstop()\n--s0_b--', out)

    def test_legacy_unit_name_becomes_id(self):
        out = pyms_compat.convert('TMCx(1342, 101, aiscript):\n--a--\ntrain(3,  Terran Siege Tank)\nstop()\n')
        self.assertIn('train(3, 5)', out)

    def test_apostrophe_name_quoted(self):
        out = pyms_compat.convert("TMCx(1342, 101, aiscript):\n--a--\nbuild(1,  Zerg Queen's Nest,  80)\nstop()\n")
        self.assertIn('build(1, "Zerg Queen\'s Nest",  80)', out)

    def test_other_words_and_comments_untouched(self):
        self.assertIn('build(1, Terran Command Center, 150)', self.out)
        self.assertIn('# goto(gen_main) stays in comments', self.out)
        self.assertTrue(self.out.startswith('# comment before scripts\n'))


if __name__ == '__main__':
    unittest.main()

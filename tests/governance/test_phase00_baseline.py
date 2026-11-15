import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MASTER=ROOT/'docs/phases/PHASE-00.md'

class Phase00BaselineTests(unittest.TestCase):
    def test_confirmed_decisions_exist_in_one_canonical_file(self):
        text=MASTER.read_text(encoding='utf-8')
        for i in range(1,9):
            self.assertIn(f'DEC-{i:03d}',text)
        self.assertIn('SOURCE OF TRUTH',text)
    def test_open_items_not_confirmed(self):
        text=MASTER.read_text(encoding='utf-8')
        for i in range(1,14):
            self.assertIn(f'OD-{i:03d}',text)
        self.assertIn('not confirmed',text.lower())
        self.assertIn('NOT APPROVED',text)
    def test_human_independent_review_required(self):
        text=MASTER.read_text(encoding='utf-8')
        self.assertIn('Human Product Owner',text)
        self.assertIn('Independent reviewer',text)
        self.assertIn('NOT formally accepted',text)
    def test_other_phase00_baselines_absent(self):
        for f in ('PRODUCT_BASELINE_V2_1.md','OPEN_DECISIONS.md','PHASE00_TOM_TAT_VI.md'):
            self.assertFalse((ROOT/'docs/requirements'/f).exists())
    def test_agent_entrypoint_points_to_master(self):
        for filename in ('AGENTS.md','CLAUDE.md'):
            self.assertIn('docs/phases/PHASE-00.md',(ROOT/filename).read_text(encoding='utf-8'))
    def test_srs_references_canonical(self):
        self.assertIn('docs/phases/PHASE-00.md',(ROOT/'docs/requirements/SRS_MASTER.md').read_text(encoding='utf-8'))

if __name__=='__main__': unittest.main()

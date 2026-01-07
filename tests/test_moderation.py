import unittest
import tempfile
import os
import json
from core.moderation import ModerationQueue

class TestModeration(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.mktemp()
        self.mod = ModerationQueue(self.temp_db)

    def tearDown(self):
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)

    def test_report_lifecycle(self):
        # 1. Report
        rid = self.mod.add_report("user1", "user2", "spam", "proof.png")
        self.assertTrue(rid.startswith("rep_"))

        queue = self.mod.get_queue()
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]['reporter'], "user1")
        self.assertEqual(queue[0]['status'], "PENDING")

        # 2. Resolve
        success = self.mod.resolve_report(rid, "admin", "WARN", "First offense")
        self.assertTrue(success)

        # Check Queue cleared
        self.assertEqual(len(self.mod.get_queue()), 0)

        # Check Log populated
        log = self.mod.get_log()
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]['resolution'], "WARN")
        self.assertEqual(log[0]['resolver'], "admin")

    def test_persistence(self):
        rid = self.mod.add_report("u1", "u2", "bad", None)

        # New instance
        mod2 = ModerationQueue(self.temp_db)
        self.assertEqual(len(mod2.get_queue()), 1)
        self.assertEqual(mod2.get_queue()[0]['id'], rid)

if __name__ == '__main__':
    unittest.main()

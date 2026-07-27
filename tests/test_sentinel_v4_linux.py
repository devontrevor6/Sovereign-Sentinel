import unittest

from sentinel_v4_linux import parse_cell_snapshot, should_alert


class SentinelV4LinuxTests(unittest.TestCase):
    def test_parse_cell_snapshot_list(self):
        payload = [{"pci": 275, "tac": 5135, "rssi": -43}]
        snap = parse_cell_snapshot(payload)
        self.assertEqual(snap["pci"], "275")
        self.assertEqual(snap["tac"], "5135")
        self.assertEqual(snap["rssi"], "-43")

    def test_should_alert_true(self):
        snap = {"pci": "275", "tac": "5135", "rssi": "-43"}
        self.assertTrue(should_alert(snap))

    def test_should_alert_false(self):
        snap = {"pci": "100", "tac": "5135", "rssi": "-43"}
        self.assertFalse(should_alert(snap))


if __name__ == "__main__":
    unittest.main()

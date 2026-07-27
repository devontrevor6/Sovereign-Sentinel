import unittest

from blackbird_linux import AccessPoint, detect_targets, parse_iw_scan_output


class BlackbirdTests(unittest.TestCase):
    def test_parse_iw_scan_output(self):
        sample = (
            "BSS d4:b9:2f:11:22:33(on wlan1)\n"
            "\tsignal: -42.00 dBm\n"
            "\tSSID: Target\n"
            "BSS aa:bb:cc:44:55:66(on wlan1)\n"
            "\tsignal: -77.00 dBm\n"
            "\tSSID: Other\n"
        )
        aps = parse_iw_scan_output(sample)
        self.assertEqual(len(aps), 2)
        self.assertEqual(aps[0].bssid, "d4:b9:2f:11:22:33")
        self.assertEqual(aps[0].ssid, "Target")
        self.assertEqual(aps[0].signal_dbm, -42.0)

    def test_detect_targets(self):
        aps = [
            AccessPoint(bssid="d4:b9:2f:11:22:33", signal_dbm=-42.0, ssid="Target"),
            AccessPoint(bssid="aa:bb:cc:44:55:66", signal_dbm=-77.0, ssid="Other"),
        ]
        hits = detect_targets(aps, ["d4:b9:2f"])
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].ssid, "Target")


if __name__ == "__main__":
    unittest.main()

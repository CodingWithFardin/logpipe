import unittest
from datetime import datetime, timezone

from logpipe.parser import parse_line
from logpipe.report import summarise


class ParseTest(unittest.TestCase):
    def test_combined_access_line(self):
        line = '1.2.3.4 - - [14/Nov/2026:10:00:00 +0000] "GET /api/x HTTP/1.1" 200 512'
        record = parse_line(line)
        self.assertEqual(record.kind, "access")
        self.assertEqual(record.fields["status"], 200)
        self.assertEqual(record.fields["path"], "/api/x")
        self.assertEqual(record.fields["size"], 512)

    def test_kv_line(self):
        record = parse_line('ts=2026-11-14 level=error msg="boom" code=500')
        self.assertEqual(record.kind, "kv")
        self.assertEqual(record.level, "error")
        self.assertEqual(record.timestamp,
                         datetime(2026, 11, 14, tzinfo=timezone.utc))
        self.assertEqual(record.fields["code"], "500")

    def test_plain_line(self):
        record = parse_line("2026-11-14T10:00:00Z warn disk low")
        self.assertEqual(record.kind, "plain")
        self.assertEqual(record.level, "warn")
        self.assertEqual(record.fields["message"], "disk low")

    def test_unknown_and_blank(self):
        self.assertEqual(parse_line("just some text").kind, "raw")
        self.assertIsNone(parse_line("   "))

    def test_bad_size_becomes_none(self):
        line = '1.2.3.4 - - [14/Nov/2026:10:00:00 +0000] "GET / HTTP/1.1" 200 -'
        self.assertIsNone(parse_line(line).fields["size"])


class ReportTest(unittest.TestCase):
    def test_summarise(self):
        lines = [
            '1.1.1.1 - - [14/Nov/2026:10:00:00 +0000] "GET /a HTTP/1.1" 200 10',
            '1.1.1.1 - - [14/Nov/2026:10:00:01 +0000] "GET /a HTTP/1.1" 500 10',
            'ts=2026-11-14 level=error msg="db down"',
        ]
        report = summarise([parse_line(l) for l in lines])
        self.assertEqual(report["total"], 3)
        self.assertEqual(report["by_status"][500], 1)
        self.assertEqual(report["top_paths"][0], ("/a", 2))
        self.assertEqual(len(report["errors"]), 1)


if __name__ == "__main__":
    unittest.main()

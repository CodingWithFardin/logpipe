"""Line parser for common access log shapes.

Handles three layouts without regex backtracking surprises:

    key=value key=value ...
    2026-11-14T10:00:00Z info message text
    1.2.3.4 - - [14/Nov/2026:10:00:00 +0000] "GET /x HTTP/1.1" 200 123
"""
import re
from datetime import datetime, timezone

COMBINED = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<stamp>[^\]]+)\] "(?P<method>[A-Z]+) (?P<path>\S+)[^"]*" '
    r'(?P<status>\d{3}) (?P<size>\S+)')
TIMESTAMP = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}:\d{2}))?")
LEVELS = {"trace", "debug", "info", "warn", "warning", "error", "fatal"}


class LogRecord:
    __slots__ = ("kind", "timestamp", "level", "fields", "raw")

    def __init__(self, kind, timestamp=None, level="", fields=None, raw=""):
        self.kind = kind
        self.timestamp = timestamp
        self.level = level
        self.fields = fields or {}
        self.raw = raw

    def __repr__(self):
        return "LogRecord(%s, %s, %s)" % (self.kind, self.level, self.timestamp)

    def __eq__(self, other):
        return (isinstance(other, LogRecord) and self.kind == other.kind
                and self.timestamp == other.timestamp and self.level == other.level
                and self.fields == other.fields)


def parse_timestamp(text):
    match = TIMESTAMP.match(text or "")
    if not match:
        return None
    day, clock = match.groups()
    return datetime.fromisoformat("%sT%s" % (day, clock or "00:00:00")).replace(tzinfo=timezone.utc)


def parse_line(line):
    """Parse one line. Unknown shapes come back as kind='raw' with no fields."""
    line = line.rstrip("\n")
    if not line.strip():
        return None

    match = COMBINED.match(line)
    if match:
        fields = match.groupdict()
        try:
            fields["status"] = int(fields["status"])
        except ValueError:
            pass
        size = fields.get("size", "")
        fields["size"] = int(size) if size.isdigit() else None
        return LogRecord("access", None, "", fields, line)

    if "=" in line and " " in line:
        pairs = {}
        for token in line.split():
            key, sep, value = token.partition("=")
            if sep and key and not key.startswith("-"):
                pairs[key] = value.strip('"')
        if pairs:
            level = pairs.get("level", "").lower()
            return LogRecord("kv", parse_timestamp(pairs.get("ts", pairs.get("time", ""))),
                             level, pairs, line)

    parts = line.split(None, 2)
    if len(parts) >= 2 and parts[1].lower() in LEVELS:
        return LogRecord("plain", parse_timestamp(parts[0]), parts[1].lower(),
                         {"message": parts[2] if len(parts) > 2 else ""}, line)

    return LogRecord("raw", None, "", {}, line)


def parse_stream(lines):
    for line in lines:
        record = parse_line(line)
        if record is not None:
            yield record

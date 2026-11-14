"""Aggregations over parsed records."""
import collections


def summarise(records):
    """Return counts by kind, level, status and the top paths."""
    by_kind = collections.Counter()
    by_level = collections.Counter()
    by_status = collections.Counter()
    by_path = collections.Counter()
    errors = []

    for record in records:
        by_kind[record.kind] += 1
        if record.level:
            by_level[record.level] += 1
        if record.level in ("error", "fatal"):
            errors.append(record.raw)
        status = record.fields.get("status")
        if isinstance(status, int):
            by_status[status] += 1
        path = record.fields.get("path")
        if path:
            by_path[path] += 1

    return {
        "total": sum(by_kind.values()),
        "by_kind": dict(by_kind),
        "by_level": dict(by_level),
        "by_status": dict(sorted(by_status.items())),
        "top_paths": by_path.most_common(5),
        "errors": errors[:10],
    }

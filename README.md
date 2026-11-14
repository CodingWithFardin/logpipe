# logpipe

A streaming log parser that normalises the three line shapes most services actually
emit, then aggregates them. Pipe `tail -f` into it, or import the parser and feed it
your own lines.

## Install

Python 3.11+, no dependencies.

```
git clone https://github.com/CodingWithFardin/logpipe.git
cd logpipe
python -m unittest discover -s tests -t .
```

## Shapes it understands

```
ts=2026-11-14 level=error msg="db down" code=500
2026-11-14T10:00:00Z warn disk low
1.2.3.4 - - [14/Nov/2026:10:00:00 +0000] "GET /api/x HTTP/1.1" 200 512
```

Anything else comes back as `kind="raw"` with the original text kept, so nothing is
silently dropped.

## Use

```python
from logpipe import parse_stream, summarise

records = parse_stream(open("access.log"))
report = summarise(records)
print(report["by_status"], report["top_paths"], report["errors"][:3])
```

`summarise` returns total counts, counts by kind and level, a status histogram, the
five busiest paths, and the first ten error lines verbatim.

## Details

- Timestamps are parsed as UTC and returned as aware datetimes; date-only values
  become midnight.
- A non-numeric size in an access line becomes `None`, not zero, so the difference
  between "0 bytes" and "unknown" survives.
- Key/value parsing ignores flags that start with `-` and strips surrounding quotes.

## Files

- `logpipe/parser.py` - line shapes and record type.
- `logpipe/report.py` - aggregation.
- `tests/` - one test per shape plus the edge cases above.

MIT, 2026.

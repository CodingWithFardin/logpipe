"""logpipe - streaming log parser with typed records and aggregation."""

from .parser import LogRecord, parse_line, parse_stream
from .report import summarise

__all__ = ["LogRecord", "parse_line", "parse_stream", "summarise"]

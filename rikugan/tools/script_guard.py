"""Shared security patterns for Python script execution tools."""

from __future__ import annotations

import re

# Patterns that indicate process execution — blocked for safety.
BLOCKED_SCRIPT_PATTERNS = [
    r"\bsubprocess\b",
    r"\bos\.system\s*\(",
    r"\bos\.popen\s*\(",
    r"\bos\.exec\w*\s*\(",
    r"\bos\.spawn\w*\s*\(",
    r"\bPopen\s*\(",
    r"\b__import__\s*\(\s*['\"]subprocess['\"]\s*\)",
]
BLOCKED_SCRIPT_RE = re.compile("|".join(BLOCKED_SCRIPT_PATTERNS))

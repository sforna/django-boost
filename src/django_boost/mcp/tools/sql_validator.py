"""
Read-only SQL query validator.

Port of the security algorithm from Laravel Boost's DatabaseQuery tool.
Ensures only read-only queries are executed (SELECT, SHOW, EXPLAIN, etc.).
"""

import re
from typing import Tuple

# Write keywords to block at statement boundaries
_WRITE_KEYWORDS = r"DELETE|UPDATE|DROP|ALTER|TRUNCATE|RENAME|CREATE|MERGE"

# Allow-listed read-only commands (uppercase)
_ALLOW_LIST = {
    "SELECT",
    "SHOW",
    "EXPLAIN",
    "DESCRIBE",
    "DESC",
    "WITH",  # Must be followed by SELECT
    "VALUES",  # Returns literal values
    "TABLE",  # PostgreSQL shorthand for SELECT *
}


def is_read_only_query(query: str) -> bool:
    """Determine if a SQL query only reads data.

    Returns True if the query is safe to execute as read-only.
    """
    structure, has_version_comment = _without_literals_and_comments(query)

    # MySQL version-gated comments are executable
    if has_version_comment:
        return False

    # Reject stacked statements (allow single trailing semicolon)
    if re.search(r";\s*\S", structure):
        return False

    # Get the first word
    token = structure.strip().split()[0] if structure.strip() else ""
    first_word = token.upper()

    if first_word not in _ALLOW_LIST:
        return False

    # WITH must be followed by SELECT
    if first_word == "WITH" and not re.search(r"\)\s*SELECT\b", structure, re.IGNORECASE):
        return False

    # Block write keywords at statement boundaries (^, after (, ), or ;)
    # INSERT(...)/REPLACE(...) as function calls remain allowed
    pattern = r"(^|[();])\s*((?:%s)\b|(?:INSERT|REPLACE)\b(?!\s*\())" % _WRITE_KEYWORDS
    if re.search(pattern, structure, re.IGNORECASE):
        return False

    # EXPLAIN ANALYZE may only target read operations
    if first_word == "EXPLAIN":
        explain_write = (
            r"^\s*EXPLAIN\s+(?:\([^)]*\)\s*|(?:ANALYZE|VERBOSE|QUERY\s+PLAN|FORMAT\s*=?\s*\w+)\s+)*"
            r"(?:%s|INSERT|REPLACE)\b" % _WRITE_KEYWORDS
        )
        if re.search(explain_write, structure, re.IGNORECASE):
            return False

    # INTO always writes
    if re.search(r"\bINTO\b", structure, re.IGNORECASE):
        return False

    return True


def _without_literals_and_comments(query: str) -> Tuple[str, bool]:
    """Remove string literals and comments from a query.

    Returns (sanitized_structure, has_version_comment).
    """
    structure = []
    state = "none"
    has_version_comment = False
    length = len(query)
    i = 0

    while i < length:
        char = query[i]
        next_char = query[i + 1] if i + 1 < length else ""

        if state == "none":
            if char in ("'", '"', "`"):
                state = {"'": "single", '"': "double", "`": "backtick"}[char]
                structure.append(" ")
            elif char == "-" and next_char == "-":
                state = "line_comment"
                structure.append(" ")
                i += 1
            elif char == "/" and next_char == "*":
                next2 = query[i + 2] if i + 2 < length else ""
                if next2 == "!":
                    # MySQL version-gated comment — executable
                    has_version_comment = True
                    structure.append(char)
                else:
                    state = "block_comment"
                    structure.append(" ")
                    i += 1
            else:
                structure.append(char)

        elif state == "line_comment":
            if char == "\n":
                state = "none"
                structure.append(char)

        elif state == "block_comment":
            if char == "*" and next_char == "/":
                state = "none"
                i += 1

        else:  # single, double, or backtick quoted
            quote = {"single": "'", "double": '"', "backtick": "`"}[state]
            if char == quote:
                if next_char == quote:
                    i += 1  # escaped quote, literal continues
                else:
                    state = "none"

        i += 1

    return "".join(structure), has_version_comment

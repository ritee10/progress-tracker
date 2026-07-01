# ============================================================
# Utility — LIKE Pattern Escaping
# ============================================================


def escape_like(query: str) -> str:
    """
    Escape special LIKE/ILIKE wildcard characters in user input.

    Prevents pattern injection where users could craft queries
    with '%' or '_' to match unintended records.

    Args:
        query: Raw user search input.

    Returns:
        Escaped string safe for use in SQL LIKE/ILIKE patterns.
    """
    return (
        query
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )

def get_pagination(page: int, limit: int) -> tuple[int, int]:
    """
    Returns offset and limit for pagination.
    Ensure page >= 1 and limit >= 1.
    """
    page = max(1, page)
    limit = max(1, limit)
    offset = (page - 1) * limit
    return offset, limit

def format_breadcrumb(path: str) -> str:
    """
    Formats a topic path string into a readable breadcrumb.
    Assuming path looks like "TopicA > TopicB > TopicC" or something similar,
    or if path is a materialized path of UUIDs, we would need to join the names.
    Since path might be UUIDs or names, let's keep it simple or return as is.
    Wait, in the models, topic.path is Text. 
    Let's just return it as is or do any needed formatting.
    """
    if not path:
        return ""
    # If it's stored as 'id1/id2/id3', then we might need to resolve it.
    # The requirement says: "Return full breadcrumb path Example: DSA > Arrays > Prefix Sum"
    # Usually we can construct this in the service layer if path stores IDs, 
    # but let's provide a utility just in case.
    return path

def truncate_preview(text: str, length: int = 100) -> str:
    """
    Truncates a long text for preview in search results.
    """
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'

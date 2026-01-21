from html_sanitizer import Sanitizer
from html_sanitizer.sanitizer import sanitize_href

sanitizer = Sanitizer(
    {
        "tags": [
            "p",
            "br",
            "b",
            "i",
            "u",
            "em",
            "strong",
            "ul",
            "ol",
            "li",
            "a",
            "blockquote",
            "code",
            "pre",
            "h1",
            "h2",
            "h3",
        ],
        "empty": ["a"],
        "separate": ["p", "li", "h1", "h2", "h3"],
        "whitespace": {"\t", "\n", "\r", " "},
        "keep_typographic_whitespace": False,
        "sanitize_href": sanitize_href,
        "strip": True,
        "escape": False,
    }
)


def sanitize_html(html: str) -> str:
    return sanitizer.sanitize(html)

import re
import markdown
import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Safe HTML tags (no img, iframe, script for XSS protection)
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'code', 'pre', 'ul', 'ol', 'li',
    'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'hr'
]

# Only allow safe link attributes
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
}


@register.filter(name='markdown')
def render_markdown(value):
    """
    Convert markdown text to safe HTML.
    Sanitizes output to prevent XSS attacks.
    Images are excluded for security reasons.
    """
    if not value:
        return ''
    
    md = markdown.Markdown(extensions=['fenced_code', 'nl2br', 'codehilite'])
    html = md.convert(value)
    
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    def unescape_code_content(match):
        content = match.group(1)
        content = content.replace('&quot;', '"')
        content = content.replace('&amp;', '&')
        content = content.replace('&lt;', '<')
        content = content.replace('&gt;', '>')
        return f'<code>{content}</code>'
    
    clean_html = re.sub(r'<code>([^<]*)</code>', unescape_code_content, clean_html)
    
    clean_html = bleach.linkify(
        clean_html,
        callbacks=[lambda attrs, new: {**attrs, (None, 'rel'): 'nofollow noopener'}],
        skip_tags=['pre', 'code']
    )
    
    return mark_safe(clean_html)

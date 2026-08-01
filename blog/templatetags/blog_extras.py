import re

import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def first_paragraph(text):
    """只取正文的第一段（用于首页预览）。

    按空行分段优先；若全篇无空行（单换行分段），则取第一个非空行。
    这样无论中英文都能保证首页只显示“开头那一段”，而不是全部内容。
    """
    if not text:
        return ""
    text = text.strip()
    # 标准段落分隔：空行
    parts = re.split(r"\n\s*\n", text)
    if len(parts) > 1:
        return parts[0].strip()
    # 无空行：按单换行，取第一个非空行
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return text


@register.filter
def markdown(text):
    """把文章正文按 Markdown 渲染为 HTML（覆盖 Obsidian 常用语法）。

    使用 extensions:
      - extra: 标题/粗体/斜体/列表/引用/链接/图片/表格/围栏代码块/脚注
      - toc:   支持 [TOC] 目录
    输出用 mark_safe 标记为安全 HTML，供模板直接渲染。
    """
    if not text:
        return ""
    html = md.markdown(text, extensions=["extra", "toc"])
    return mark_safe(html)

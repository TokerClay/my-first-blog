import os

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Post

# 首页列表
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

# 文章详情
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@staff_member_required
def import_md(request):
    """拖 / 选 .md 文件，直接生成一篇博文（仅 staff 可用）。"""
    if request.method == "POST":
        md_file = request.FILES.get("md_file")
        if not md_file:
            messages.error(request, "没有收到文件，请先选择或拖入一个 .md 文件。")
            return redirect("import_md")

        ext = os.path.splitext(md_file.name)[1].lower()
        if ext not in (".md", ".markdown", ".txt"):
            messages.error(request, "只支持 .md / .markdown / .txt 文件。")
            return redirect("import_md")

        try:
            raw = md_file.read().decode("utf-8")
        except UnicodeDecodeError:
            messages.error(request, "文件解码失败，请确认是 UTF-8 编码的 Markdown。")
            return redirect("import_md")

        title, body = _parse_markdown_file(raw, fallback_title=os.path.splitext(md_file.name)[0])
        post = Post.objects.create(
            title=title[:200],
            text=body,
            author=request.user,
            published_date=timezone.now(),
        )
        messages.success(request, f"已导入《{title}》")
        return redirect("post_detail", pk=post.pk)

    return render(request, "blog/import_md.html")

def _parse_markdown_file(content, fallback_title):
    """从 Markdown 文本里取标题与正文。

    - 有 YAML frontmatter 且含 title: 则用其作标题；
    - 否则取第一个 '# 标题' 行；
    - 再否则用文件名作标题。
    返回 (title, body)，body 为去掉 frontmatter 后的正文。
    """
    content = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    title = ""
    body = content

    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            fm = content[3:end].strip()
            for line in fm.splitlines():
                if line.lower().startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"').strip("'")
            body = content[end + 4:].strip()

    if not title:
        for line in body.splitlines():
            line = line.strip()
            if line.startswith("# "):
                title = line[2:].strip()
                break

    if not title:
        title = fallback_title

    return title, body

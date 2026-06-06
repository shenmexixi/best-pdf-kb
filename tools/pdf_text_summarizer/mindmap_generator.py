import re
from tools.pdf_text_summarizer.models import PaperSummary
from tools.pdf_text_summarizer.llm.base import LLMBackend

MINDMAP_PROMPT = """基于这篇论文的结构和摘要，生成一份 Markdown 嵌套列表格式的中文思维导图。

论文主题: {one_liner}

各章节及要点：
{sections_text}

请输出 Markdown 嵌套列表（使用 - 作为列表项，2空格缩进表示层级）。
思维导图要求：
- 以论文标题/主题为根节点
- 按逻辑分组相关概念
- 包含关键发现和方法
- 每个节点简洁（最多15个字）
- 2-4层深度

只输出 Markdown 列表，不要输出其他文字或代码块标记。
"""

async def generate_mindmap(paper_summary: PaperSummary, llm_backend: LLMBackend) -> str:
    sections_text = _format_for_mindmap(paper_summary)
    prompt = MINDMAP_PROMPT.format(one_liner=paper_summary.one_liner, sections_text=sections_text)
    response = await llm_backend.complete(prompt)
    return _clean_mindmap_response(response)

def _format_for_mindmap(summary: PaperSummary) -> str:
    parts = []
    for s in summary.sections:
        points = ", ".join(s.key_points) if s.key_points else "N/A"
        parts.append(f"- {s.title}: {s.summary} (Key: {points})")
    return "\n".join(parts)

def _clean_mindmap_response(response: str) -> str:
    text = response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    return text

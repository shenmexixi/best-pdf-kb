import json, re
from tools.pdf_text_summarizer.models import SectionSummary, PaperSummary
from tools.pdf_text_summarizer.llm.base import LLMBackend

OVERALL_PROMPT = """你正在对一篇科研论文进行深度解读和结构化总结。

以下是论文各章节的摘要：
{sections_text}

请按照论文的研究逻辑（而非章节顺序）进行重组和总结：
- 研究背景与问题是什么？
- 提出了什么方法/方案？为什么这样设计？
- 关键结果和发现是什么？
- 这项工作的意义和贡献是什么？

请用中文输出严格 JSON 格式（不要输出其他内容）：
{{
  "one_liner": "一句话概括论文的核心贡献（不超过30字）",
  "abstract_summary": "150-250字的论文摘要，按研究逻辑组织",
  "detailed_summary": "500-1000字的深度解读，按逻辑展开而非按章节罗列",
  "key_contributions": ["核心贡献1", "核心贡献2"],
  "methodology": "方法论简述，包括为什么选择这种方法",
  "main_findings": ["关键发现1（包含具体数据或结论）", "关键发现2"]
}}
"""

GROUP_SUMMARY_PROMPT = """以下是论文部分章节的摘要，请归纳为一段简洁的总结（200字以内）：

{group_text}

只输出总结文本，不要输出其他内容。
"""

# Max characters for all section summaries combined before triggering batched mode
BATCH_THRESHOLD = 6000
# Number of sections per batch
BATCH_SIZE = 6


async def generate_overall_summary(section_summaries: list[SectionSummary], llm_backend: LLMBackend) -> PaperSummary:
    sections_text = _format_sections(section_summaries)

    if len(sections_text) <= BATCH_THRESHOLD:
        # Short enough: single-call summary
        prompt = OVERALL_PROMPT.format(sections_text=sections_text)
        response = await llm_backend.complete(prompt)
    else:
        # Long paper: batch sections → intermediate summaries → final summary
        condensed = await _batched_summarize(section_summaries, llm_backend)
        prompt = OVERALL_PROMPT.format(sections_text=condensed)
        response = await llm_backend.complete(prompt)

    data = _parse_overall_response(response)
    return PaperSummary(
        one_liner=data.get("one_liner", ""),
        abstract_summary=data.get("abstract_summary", ""),
        detailed_summary=data.get("detailed_summary", ""),
        key_contributions=data.get("key_contributions", []),
        methodology=data.get("methodology", ""),
        main_findings=data.get("main_findings", []),
        sections=section_summaries,
    )


async def _batched_summarize(sections: list[SectionSummary], llm_backend: LLMBackend) -> str:
    """Split sections into batches, summarize each batch, then concatenate."""
    batches = []
    for i in range(0, len(sections), BATCH_SIZE):
        batches.append(sections[i:i + BATCH_SIZE])

    batch_summaries = []
    for batch in batches:
        group_text = _format_sections(batch)
        prompt = GROUP_SUMMARY_PROMPT.format(group_text=group_text)
        response = await llm_backend.complete(prompt)
        batch_summaries.append(response.strip())

    return "\n\n".join(
        f"[Group {i+1}] {s}" for i, s in enumerate(batch_summaries)
    )


def _format_sections(sections: list[SectionSummary]) -> str:
    parts = []
    for s in sections:
        points = "; ".join(s.key_points) if s.key_points else ""
        parts.append(f"## {s.title}\nSummary: {s.summary}\nKey points: {points}")
    return "\n\n".join(parts)


def _parse_overall_response(response: str) -> dict:
    text = response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    try:
        return json.loads(text)
    except (json.JSONDecodeError, KeyError):
        return {"one_liner": text[:200], "abstract_summary": text, "detailed_summary": text, "key_contributions": [], "methodology": "", "main_findings": []}

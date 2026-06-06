import json
import re
from tools.pdf_text_summarizer.llm.base import LLMBackend


DOMAIN_EXPERT_PROMPT = """你是一位{domain}领域的资深专家。请对以下科研论文解读文章进行专业审核。

文章内容（HTML）：
{html_content}

请从以下角度评审：
1. 内容准确性：是否有事实错误或误导性表述？
2. 专业深度：解读是否足够深入？是否遗漏了重要概念？
3. 逻辑完整性：论证链条是否完整？因果关系是否正确？

请用中文输出严格 JSON 格式（不要输出其他内容）：
{{
  "score": 1-10,
  "issues": ["问题1：具体描述", "问题2：具体描述"],
  "suggestions": ["建议1：具体修改方案", "建议2：具体修改方案"],
  "highlights": ["亮点1", "亮点2"]
}}
"""

EDITOR_PROMPT = """你是一位专业的科技写作编辑。请对以下科研论文解读文章进行编辑审核。

文章内容（HTML）：
{html_content}

请从以下角度评审：
1. 语言风格：是否专业流畅？是否有语病或表述不当？
2. 结构排版：段落划分是否合理？层级是否清晰？
3. 图文配合：图片位置是否合适？图片讲解是否充分？
4. 逻辑连续性：各部分之间是否有良好的过渡和衔接？
5. 读者体验：整体可读性如何？

请用中文输出严格 JSON 格式（不要输出其他内容）：
{{
  "score": 1-10,
  "issues": ["问题1：具体描述", "问题2：具体描述"],
  "suggestions": ["建议1：具体修改方案", "建议2：具体修改方案"],
  "highlights": ["亮点1", "亮点2"]
}}
"""

REVISION_PROMPT = """请根据以下专家评审意见，修改这篇科研论文解读文章。

原始文章（HTML）：
{html_content}

领域专家意见：
{domain_review}

写作编辑意见：
{editor_review}

请综合以上意见进行修改，输出修改后的完整 HTML（从 <!DOCTYPE html> 开始）。
要求：
1. 修复所有指出的问题
2. 采纳合理的建议
3. 保留原文的亮点
4. 不要删除图片引用
5. 保持整体结构完整

输出完整的修改后 HTML，不要输出其他内容。
"""


async def expert_review(
    html_content: str,
    domain: str,
    llm_backend: LLMBackend,
) -> dict:
    """Run two-expert review on HTML content.

    Returns:
        {
            "domain_review": {...},
            "editor_review": {...},
            "revised_html": "..."
        }
    """
    # Stage 1: Domain expert review
    domain_prompt = DOMAIN_EXPERT_PROMPT.format(domain=domain, html_content=html_content)
    domain_response = await llm_backend.complete(domain_prompt)
    domain_review = _parse_review_response(domain_response)

    # Stage 2: Writing editor review
    editor_prompt = EDITOR_PROMPT.format(html_content=html_content)
    editor_response = await llm_backend.complete(editor_prompt)
    editor_review = _parse_review_response(editor_response)

    # Stage 3: Revision based on feedback
    domain_text = json.dumps(domain_review, ensure_ascii=False, indent=2)
    editor_text = json.dumps(editor_review, ensure_ascii=False, indent=2)
    revision_prompt = REVISION_PROMPT.format(
        html_content=html_content,
        domain_review=domain_text,
        editor_review=editor_text,
    )
    revised_html = await llm_backend.complete(revision_prompt)
    revised_html = _clean_html(revised_html)

    return {
        "domain_review": domain_review,
        "editor_review": editor_review,
        "revised_html": revised_html,
    }


def _parse_review_response(response: str) -> dict:
    text = response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    try:
        return json.loads(text)
    except (json.JSONDecodeError, KeyError):
        return {"score": 0, "issues": [text[:200]], "suggestions": [], "highlights": []}


def _clean_html(response: str) -> str:
    text = response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    return text


def infer_domain(summary: dict) -> str:
    """Infer the academic domain from summary content."""
    import re as _re
    text = (summary.get("one_liner", "") + " " + summary.get("methodology", "")).lower()
    # Use word-boundary matching for ASCII keywords to avoid substring false positives
    domain_keywords = {
        "计算化学": ["wavefunction", "quantum", "molecular", "electron", "orbital", "dft", "化学"],
        "机器学习": ["neural", "deep learning", "model", "training", "network", "机器学习", "算法"],
        "材料科学": ["material", "crystal", "alloy", "polymer", "纳米", "材料"],
        "生物信息学": ["protein", "gene", "genome", "dna", "rna", "生物"],
        "物理学": ["physics", "quantum", "field", "particle", "物理"],
    }
    for domain, keywords in domain_keywords.items():
        for kw in keywords:
            # Use word boundaries for ASCII keywords
            if kw.isascii():
                if _re.search(r'\b' + _re.escape(kw) + r'\b', text):
                    return domain
            else:
                if kw in text:
                    return domain
    return "科学研究"

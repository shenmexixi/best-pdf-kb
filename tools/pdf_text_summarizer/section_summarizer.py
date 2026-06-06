import asyncio, json, re
from tools.pdf_text_summarizer.models import Section, SectionSummary
from tools.pdf_text_summarizer.llm.base import LLMBackend

SECTION_PROMPT = """请对以下科研论文章节进行深入讲解。要求：
1. 不要只是简单复述，要解释这部分的核心逻辑和意义
2. 如果涉及方法，说明为什么选择这种方法
3. 如果涉及结果，解读数据说明了什么

章节标题: {title}
内容:
{content}

请用中文输出严格 JSON 格式（不要输出其他内容）：
{{
  "summary": "3-5句话对该章节核心内容的深度讲解，而非简单概括",
  "key_points": ["要点1：包含具体信息", "要点2：包含具体信息"]
}}
"""

MERGE_PROMPT = """以下是同一章节分段摘要的结果，请将它们合并为一个完整、连贯的摘要。

章节标题: {title}

各段摘要：
{chunk_summaries}

请用中文输出严格 JSON 格式（不要输出其他内容）：
{{
  "summary": "合并后的3-5句话深度讲解",
  "key_points": ["要点1：包含具体信息", "要点2：包含具体信息"]
}}
"""

SKIP_TITLES = {"references", "acknowledgments", "acknowledgements", "bibliography"}

# Chunk size for long sections (characters)
CHUNK_MAX_CHARS = 2500
CHUNK_OVERLAP = 200


async def summarize_sections(
    sections: list[Section], llm_backend: LLMBackend, min_length: int = 100, max_concurrent: int = 3,
) -> list[SectionSummary]:
    flat = _flatten_sections(sections)
    to_summarize = [s for s in flat if not _should_skip_section(s.title, s.content, min_length)]
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [_summarize_one(s, llm_backend, semaphore) for s in to_summarize]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


async def _summarize_one(section: Section, llm_backend: LLMBackend, semaphore: asyncio.Semaphore) -> SectionSummary | None:
    async with semaphore:
        try:
            content = section.content
            if len(content) <= CHUNK_MAX_CHARS:
                # Short section: single call
                prompt = SECTION_PROMPT.format(title=section.title, content=content)
                response = await llm_backend.complete(prompt)
                summary, key_points = _parse_section_response(response)
            else:
                # Long section: chunk → summarize each → merge
                chunks = _chunk_content(content, CHUNK_MAX_CHARS, CHUNK_OVERLAP)
                chunk_results = []
                for i, chunk in enumerate(chunks):
                    chunk_label = f"{section.title} (part {i+1}/{len(chunks)})"
                    prompt = SECTION_PROMPT.format(title=chunk_label, content=chunk)
                    response = await llm_backend.complete(prompt)
                    s, kp = _parse_section_response(response)
                    chunk_results.append({"summary": s, "key_points": kp})

                # Merge chunk summaries
                chunk_summaries_text = "\n\n".join(
                    f"Part {i+1}: {r['summary']}\n要点: {'; '.join(r['key_points'])}"
                    for i, r in enumerate(chunk_results)
                )
                merge_prompt = MERGE_PROMPT.format(
                    title=section.title,
                    chunk_summaries=chunk_summaries_text,
                )
                merge_response = await llm_backend.complete(merge_prompt)
                summary, key_points = _parse_section_response(merge_response)

            return SectionSummary(title=section.title, level=section.level, summary=summary, key_points=key_points)
        except Exception:
            return None


def _chunk_content(content: str, max_chars: int = 2500, overlap: int = 200) -> list[str]:
    """Split long content into overlapping chunks, breaking at paragraph boundaries."""
    if len(content) <= max_chars:
        return [content]

    paragraphs = content.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 > max_chars and current_chunk:
            chunks.append(current_chunk.strip())
            # Keep overlap from end of previous chunk
            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:] + "\n\n" + para
            else:
                current_chunk = para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # Fallback: if paragraph-based splitting produced no chunks or a single huge chunk
    if len(chunks) <= 1 and len(content) > max_chars:
        chunks = []
        for i in range(0, len(content), max_chars - overlap):
            chunks.append(content[i:i + max_chars])

    return chunks


def _should_skip_section(title: str, content: str, min_length: int) -> bool:
    if title.lower().strip() in SKIP_TITLES:
        return True
    if len(content.strip()) < min_length:
        return True
    return False


def _flatten_sections(sections: list[Section]) -> list[Section]:
    result = []
    for s in sections:
        result.append(s)
        if s.children:
            result.extend(_flatten_sections(s.children))
    return result


def _parse_section_response(response: str) -> tuple[str, list[str]]:
    text = response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    try:
        data = json.loads(text)
        key_points = data.get("key_points", [])
        if key_points and not isinstance(key_points[0], str):
            key_points = [str(p) for p in key_points]
        return data.get("summary", ""), key_points
    except (json.JSONDecodeError, KeyError):
        return text, []

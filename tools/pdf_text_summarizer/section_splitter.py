import re
from tools.pdf_text_summarizer.models import Section

def split_sections(markdown_path: str) -> list[Section]:
    """将 markdown 文件按标题切分为章节树。"""
    with open(markdown_path, encoding="utf-8") as f:
        lines = f.readlines()

    raw_sections: list[tuple[int, str, list[str]]] = []
    current_level = 0
    current_title = ""
    current_lines: list[str] = []

    for line in lines:
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            if current_title or current_lines:
                raw_sections.append((current_level, current_title, current_lines))
            current_level = len(heading_match.group(1))
            current_title = heading_match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_title or current_lines:
        raw_sections.append((current_level, current_title, current_lines))

    # Handle preamble
    if raw_sections and raw_sections[0][0] == 0 and raw_sections[0][1] == "":
        content = "".join(raw_sections[0][2]).strip()
        if content:
            raw_sections[0] = (1, "(Preamble)", raw_sections[0][2])
        else:
            raw_sections.pop(0)

    return _build_tree(raw_sections)

def _build_tree(raw_sections: list[tuple[int, str, list[str]]]) -> list[Section]:
    if not raw_sections:
        return []

    root_sections: list[Section] = []
    stack: list[Section] = []

    for level, title, content_lines in raw_sections:
        if level == 0:
            level = 1
        content = "".join(content_lines).strip()
        section = Section(title=title, level=level, content=content)

        while stack and stack[-1].level >= level:
            stack.pop()

        if stack:
            stack[-1].children.append(section)
        else:
            root_sections.append(section)

        stack.append(section)

    return root_sections

from dataclasses import dataclass, field

@dataclass
class Section:
    title: str
    level: int
    content: str
    children: list["Section"] = field(default_factory=list)

@dataclass
class SectionSummary:
    title: str
    level: int
    summary: str
    key_points: list[str]

@dataclass
class PaperSummary:
    one_liner: str
    abstract_summary: str
    detailed_summary: str
    key_contributions: list[str]
    methodology: str
    main_findings: list[str]
    sections: list[SectionSummary]

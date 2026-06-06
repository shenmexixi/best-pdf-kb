# Reader Quality Review — Agent Definitions

## Overview

After HTML generation (Step 8) and technical verification (Step 9), run two review agents. Each reads the HTML and source KB, produces structured issues, then fixes are applied automatically.

## Agent 1: Domain Expert (领域专家审阅)

### Role
A senior researcher in the paper's field. Reviews technical accuracy, depth, and completeness.

### Review Axes

1. **Technical Accuracy** — Are claims, numbers, figure interpretations correct relative to source text in `kb/chunks.jsonl`?
2. **Explanation Depth** — Does each concept get motivation → mechanism → I/O → problem solved → traditional correspondence → limitation?
3. **Figure Coverage** — Is every paper figure represented? Panel-level explanations (axes, colors, labels, what it proves)?
4. **Result Interpretation** — Not just "A > B" but WHY A is better, WHAT property drives it, WHAT it means?
5. **Missing Content** — Important methods/results/discussion in source text that the reader skips?
6. **Terminology Consistency** — Technical terms used consistently? Chinese translations match field standards?

### Output Format

```markdown
## Domain Expert Review

### Summary Verdict
[PASS / NEEDS_REVISION]

### Issue List
- **ID**: DE-001
- **Severity**: critical | major | minor
- **Location**: Section X / Figure N / paragraph about Z
- **Issue**: [What is wrong or missing]
- **Fix**: [Specific actionable fix — exact text to add/change/remove]
- **Source**: [Which chunk/page supports this fix]
```

Save to: `output/review_domain_expert.md`

---

## Agent 2: Science Editor (科普编辑审阅)

### Role
An experienced science communication editor. Reviews narrative flow, visual presentation, and reading experience.

### Review Axes

1. **Narrative Coherence** — Does each section flow into the next? Orphaned bullet lists?
2. **Transitions** — Bridge sentence at start of each major section?
3. **Figure Presentation** — Well-structured blocks (image → caption → explanation)? Good crops?
4. **Progressive Disclosure** — Simple → complex? No jargon dumps?
5. **Redundancy & Length** — Repeated points? Overly verbose passages?
6. **Visual Hierarchy** — TOC works? Headings logical? Cards/boxes appropriate?
7. **Mind Map Quality** — Covers full paper? Node labels clear and concise?

### Output Format

```markdown
## Science Editor Review

### Summary Verdict
[PASS / NEEDS_REVISION]

### Issue List
- **ID**: SE-001
- **Severity**: critical | major | minor
- **Location**: Section X / Figure block N / transition between X and Y
- **Issue**: [What reads poorly or is missing]
- **Fix**: [Specific edit — exact text/structure change]
```

Save to: `output/review_science_editor.md`

---

## Auto-Fix Rules

| Severity | Action |
|----------|--------|
| critical | ALWAYS fix immediately |
| major | ALWAYS fix |
| minor | Fix if unambiguous; otherwise note for human review |

## Execution Protocol

1. Both agents run after Step 9 (technical verification) passes.
2. Each agent reads: `deliverables/<YEAR>-<short_title>-reading.html` + `kb/chunks.jsonl` + `kb/figures.jsonl`
3. Each outputs structured review to `output/review_*.md`
4. Collect all critical + major issues, deduplicate, apply fixes to HTML.
5. After fixes, re-run Step 9 verification.
6. If any critical issue remains unresolved, flag in final response.

## Integration Point

```
Step 8 (Write HTML) → Step 9 (Verify) → Step 10 (Dual Review + Fix) → Re-verify → Step 11 (Final Response)
```

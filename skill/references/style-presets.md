# Style Presets

## Overview

Style presets control the tone, depth, and presentation strategy of the HTML reader. The user chooses a preset before processing begins. Default is `academic`.

## Preset: `academic`

**Target audience:** 研究人员、审稿人、同行研究者

**Tone rules:**
- 正式学术语言，避免口语化表达
- 引用准确，标注具体 Section/Figure/Table 编号
- 不简化数学表述，保留公式细节
- 使用领域标准术语（附英文原文）
- 结论措辞审慎（"表明"优于"证明"）

**Depth rules:**
- 每个技术设计完整讲解六要素（动机/输入输出/机制/解决问题/传统对应/局限）
- 实验结果包含具体数值、统计显著性、与 baseline 的精确对比
- 消融实验逐项分析
- 局限性和未来工作不回避

**Section emphasis:**
- §4 方法设计：最详细（50-60% 篇幅权重）
- §5 实验结果：详细，含定量对比
- §3 背景：精炼，假设读者有基础

---

## Preset: `technical`

**Target audience:** 工程师、技术博客读者、实现者

**Tone rules:**
- 深度讲解但允许类比到工程实践
- 关注"怎么做"和"为什么这样做"
- 可引入代码片段、伪代码或配置示例
- 使用 tech-card 组件展示关键参数/超参

**Depth rules:**
- 架构讲解侧重 module 边界和 I/O 接口
- 关注实现细节（训练配置、硬件要求、推理时间）
- 对比 baseline 时侧重"什么场景下选哪个"
- 可省略纯理论推导，保留结论

**Section emphasis:**
- §4 方法设计：详细，含实现视角
- §5 实验：聚焦可复现的关键参数
- §7 总结：含"如果你要用这个方法"的实践建议

---

## Preset: `popular`

**Target audience:** 跨学科读者、研究生新手、科普爱好者

**Tone rules:**
- 先讲直觉再讲细节（"想象一下..."）
- 大量类比到日常经验
- 术语首次出现时用括号解释
- 避免未经解释的缩写堆叠
- 语言温暖但不失准确

**Depth rules:**
- 渐进式：每个概念先用一句话说清本质
- 然后再展开细节（对想深入的读者）
- 数字尽量给直观对比（"相当于..."）
- 可省略不影响理解的数学公式

**Section emphasis:**
- §1 阅读导向：更详细，明确告诉读者"为什么值得读"
- §3 背景：比 academic 更展开，不假设读者有基础
- §4 方法：重直觉，用类比先铺底
- §7 总结：更强调"这对你意味着什么"

---

## How Presets Affect HTML

| Element | academic | technical | popular |
|---------|----------|-----------|---------|
| meta-card | 完整学术信息 | 精简+实现链接 | 精简+一句话hook |
| tech-card 数量 | 多（每个设计） | 多（含参数表） | 少（仅核心） |
| formula 组件 | 保留完整公式 | 简化或伪代码 | 仅关键公式+解释 |
| result-highlight | 精确数值 | 数值+适用场景 | 数值+直观对比 |
| 图片讲解 | panel级完整 | panel级+实现视角 | 整图+关键要点 |
| 思维导图 | 6分支标准 | 6分支+实现路径 | 5分支精简 |
| 术语表 | 完整附英文 | 选择性含实现笔记 | 精选核心+解释 |

## Prompt Integration

When generating HTML content, prepend the style instructions to the LLM prompt:

```
[Style preset: {preset_name}]
{preset_tone_rules}
{preset_depth_rules}

Now generate Section {N}: {section_title}...
```

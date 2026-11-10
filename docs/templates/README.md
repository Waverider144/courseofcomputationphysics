# Chapter Templates / 章节模板

[Co-author Guidelines](../../CONTRIBUTING.md) · [合作者指南](../../CONTRIBUTING.zh-CN.md) · [AI prompts](../ai-prompts.md) · [中文 Prompt](../ai-prompts.zh-CN.md)

These are input fragments for the existing books, not standalone documents. Select the target volume and language, fill the approved content, remove unused optional blocks, and assign a unique chapter label before integration. Author placeholders remain unfilled until author review.

这些文件供现有主文件输入，不是独立文档。按卷册与语言选择模板，填写已确认内容，删去不需要的可选区，并在接入前指定唯一章节标签。尚未经作者确认的补充保持占位。

| Volume / 卷册 | Chinese / 中文 | English / 英文 | Existing interface / 现有接口 |
| --- | --- | --- | --- |
| 0 | [vol0.zh-CN.tex](vol0.zh-CN.tex) | [vol0.en.tex](vol0.en.tex) | `learninggoals`; `conceptbridge`; `aiexercise`; `studyroute{omissions}{terms}` |
| I | [vol1.zh-CN.tex](vol1.zh-CN.tex) | [vol1.en.tex](vol1.en.tex) | `learninggoals`; `conceptbridge`; `aiexercise`; `studyroute{omissions}{terms}{prompt}` |
| II | [vol2.zh-CN.tex](vol2.zh-CN.tex) | [vol2.en.tex](vol2.en.tex) | `chaptersummary`; `askai`; `studentinput`; `checkpoint`; `engineernote`; three-argument `studyroute` |

## Integration / 接入

1. **Volumes 0 and I:** place the chapter in the matching language's chapter tree and add its input at the agreed position in the main file. Reuse that edition's preamble and bibliography. For a section-sized contribution, retain the relevant blocks without adding a chapter.
2. **Volume II:** insert the agreed content into the matching monolithic source. Its preamble is at the top of that file. Preserve the special numbering around Chapter 5.5; the template uses an ordinary chapter and does not alter counters.
3. **All volumes:** align the two languages, update references and affected tests, then build using the root README. Review rendered boxes, equations, page breaks, and links.

1. **第 0、1 卷：**章节放入对应语言的目录，在约定的主文件位置加入输入，复用本版 preamble 与文献。节级贡献只保留需要的区域。
2. **第 2 卷：**将约定内容接入对应单文件源码，沿用文件顶部的 preamble。保留第 5.5 章附近的特殊编号；模板仅使用普通章，不调整计数器。
3. **所有卷：**同步中英文，更新引用与受影响的测试，再按根目录 README 构建，检查提示框、公式、分页和链接。

## Optional Blocks / 可选区域

- `conceptbridge` takes three arguments: question, author supplement, and conceptual connection. The templates leave the supplement explicitly unfilled. Retain approved supplements when editing existing chapters.
- Volume II has no `authornote` or `conceptbridge`. Its draft author input is a plain paragraph with the same three fields. `studentinput` is for the reader's answer, `checkpoint` for a conceptual check, and `engineernote` for implementation implications.
- Retain a callout only when its role is needed. No template supplies physical claims, fabricated citations, benchmark values, or completed author motivation.

- `conceptbridge` 的三个参数是潜在疑问、作者补充、核心概念联系。模板显式保留空缺；编辑已有章节时保留已确认的作者补充。
- 第 2 卷没有 `authornote` 与 `conceptbridge`。模板用普通段落标记作者输入；`studentinput` 留给读者作答，`checkpoint` 检查理解，`engineernote` 说明实现影响。
- 根据内容需要保留提示区。模板不提供新的物理主张、虚构引文、性能数值或已填写的作者动机。

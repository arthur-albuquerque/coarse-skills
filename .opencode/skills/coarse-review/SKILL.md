---
name: coarse-review
description: >
  Produce a rigorous academic peer review of a research paper, manuscript, or preprint.
  Supports markdown (.md), text (.txt), LaTeX (.tex), DOCX, HTML, and EPUB formats.
  Uses your OpenCode subscription for all LLM reasoning — no OpenRouter API key needed.
  For PDF inputs, extract text first (the skill will guide you). Takes 5-15 minutes.
allowed-tools: Read, Write, Bash, task
argument-hint: <paper-path>
---

# coarse-review (OpenCode)

Runs the **full coarse review pipeline** using your OpenCode subscription. No OpenRouter API key needed. For text/markdown inputs, the pipeline runs entirely through OpenCode's native agent system.

## Prerequisites

- **OpenCode** installed and configured (you're already using it)
- **Python 3.10+** for structure parsing (optional but recommended)
- **For PDF inputs**: Extract text first using any PDF-to-text tool, or use the `split-pdf` skill to convert to markdown

## When to Use

Invoke this skill when the user asks to:
- Review, critique, or referee an academic paper
- Provide feedback on a manuscript or preprint
- Check a paper for errors, gaps, or improvements

**Do NOT use** for: code review, blog posts, non-academic documents, or papers shorter than 2 pages.

## Input Format

The argument should be a path to the paper file:
- `.md` / `.markdown` — Best format, native support
- `.txt` — Plain text, native support
- `.tex` — LaTeX source, native support
- `.docx`, `.html`, `.epub` — Supported via python-docx / html.parser
- `.pdf` — **Not directly supported**. Convert first (see PDF conversion below)

## Pipeline Overview

The review runs in 6 phases:
1. **Load & Parse** — Read file, split into sections
2. **Structure Analysis** — Identify title, abstract, sections, domain
3. **Parallel Review Agents** — Overview + per-section reviews (launched via `task`)
4. **Cross-Section Synthesis** — Check consistency between results and discussion
5. **Editorial Pass** — Filter duplicates, contradictions, low-quality comments
6. **Output** — Render final markdown review

## Step 1: Load Paper

**Get the paper path from the user.** If not provided in the argument, ask for it.

```bash
# Verify file exists and check size
ls -lh "<paper_path>"
```

If the file does not exist, ask the user for the correct path.

If the file is a PDF (`.pdf` extension), stop and tell the user:
> PDF inputs require text extraction first. Options:
> 1. Use `pdftotext` or similar to extract text to a `.txt` or `.md` file
> 2. Use the `split-pdf` skill to convert the PDF to structured markdown
> 3. If you have a pre-extracted markdown file, pass that instead
> 
> Which would you like to do?

## Step 2: Parse Structure

Read the paper file using the `Read` tool. Then parse its structure:

### Extract Title
- First non-empty line if it looks like a title (no heading marker, substantial length)
- Or first `# ` heading
- Or first line of the file

### Extract Abstract
- Look for a section titled "Abstract", "Summary", or "Overview" (case-insensitive)
- Capture all text until the next heading

### Split into Sections
Split the paper into sections using markdown headings (`#`, `##`, `###`). For each section, record:
- **Title**: The heading text
- **Type**: One of: ABSTRACT, INTRODUCTION, RELATED_WORK, METHODOLOGY, RESULTS, DISCUSSION, CONCLUSION, APPENDIX, REFERENCES, OTHER
- **Text**: Full body text of the section
- **Math content**: True if the section contains LaTeX math (`$...$`, `\[...\]`, `\begin{equation}`)

Use a simple regex or python script for splitting. Here's a helper approach:

```bash
python3 << 'PYEOF'
import re, json, sys

def parse_paper(text):
    lines = text.split('\n')
    title = lines[0].strip() if lines else "Untitled"
    
    # Find abstract
    abstract = ""
    in_abstract = False
    for i, line in enumerate(lines):
        if re.match(r'^(?i)#*\s*abstract', line):
            in_abstract = True
            continue
        if in_abstract:
            if re.match(r'^#{1,4}\s', line):
                break
            abstract += line + "\n"
    
    # Split into sections by headings
    sections = []
    current_title = ""
    current_text = []
    current_level = 0
    
    for line in lines:
        m = re.match(r'^(#{1,4})\s+(.+)$', line)
        if m:
            if current_title:
                sections.append({
                    "title": current_title,
                    "level": current_level,
                    "text": '\n'.join(current_text).strip()
                })
            current_title = m.group(2).strip()
            current_level = len(m.group(1))
            current_text = []
        else:
            current_text.append(line)
    
    if current_title:
        sections.append({
            "title": current_title,
            "level": current_level,
            "text": '\n'.join(current_text).strip()
        })
    
    # Classify section types
    type_map = {
        "abstract": "ABSTRACT",
        "introduction": "INTRODUCTION",
        "related work": "RELATED_WORK",
        "literature": "RELATED_WORK",
        "background": "RELATED_WORK",
        "method": "METHODOLOGY",
        "methodology": "METHODOLOGY",
        "approach": "METHODOLOGY",
        "model": "METHODOLOGY",
        "result": "RESULTS",
        "experiment": "RESULTS",
        "discussion": "DISCUSSION",
        "conclusion": "CONCLUSION",
        "summary": "CONCLUSION",
        "appendix": "APPENDIX",
        "reference": "REFERENCES",
        "bibliography": "REFERENCES",
    }
    
    for sec in sections:
        sec_title_lower = sec["title"].lower()
        sec["type"] = "OTHER"
        for keyword, stype in type_map.items():
            if keyword in sec_title_lower:
                sec["type"] = stype
                break
        sec["math"] = bool(re.search(r'(\$[^$]+\$|\\\[|\\begin\{equation)', sec["text"]))
    
    return {
        "title": title,
        "abstract": abstract.strip(),
        "sections": sections
    }

if __name__ == "__main__":
    text = sys.stdin.read()
    result = parse_paper(text)
    print(json.dumps(result, indent=2))
PYEOF
```

Save this script to a temporary file, run it with the paper text piped in, and capture the JSON output.

## Step 3: Launch Parallel Review Agents

Use `task` with `run_in_background=true` to launch multiple review agents in parallel. Each agent receives the full paper text plus specific instructions.

### Agent A: Overview Review

Launch one task for the high-level overview:

```
task(category="deep", load_skills=[], run_in_background=true, prompt="""
You are an expert peer reviewer. Review this academic paper and provide 4-6 high-level macro issues.

TITLE: <title>
ABSTRACT: <abstract>
FULL TEXT:
<paper_text>

For each issue, provide:
1. A concise title (5-8 words)
2. A detailed paragraph explaining the issue, its significance, and what the authors should do

Focus on:
- Major conceptual gaps or flaws
- Methodological concerns
- Missing connections to literature
- Structural problems
- Claims that are unsupported or overreached

Write as a constructive but direct colleague. Be specific — cite section numbers or line ranges where possible. Do NOT use generic phrases like "further research is needed."

Return your response as plain text with each issue as:
### Issue N: <title>
<detailed paragraph>
""")
```

### Agent B: Per-Section Reviews

Launch one task per major section (INTRODUCTION, METHODOLOGY, RESULTS, DISCUSSION, CONCLUSION). Skip REFERENCES and APPENDIX unless they contain substantive content.

For each section task:

```
task(category="deep", load_skills=[], run_in_background=true, prompt="""
You are an expert peer reviewer. Review this specific section of an academic paper.

PAPER TITLE: <title>
ABSTRACT: <abstract>
SECTION TITLE: <section_title>
SECTION TYPE: <section_type>
SECTION TEXT:
<section_text>

Provide 3-8 detailed comments on this section. For each comment:
1. **Quote**: A verbatim quote from the section (1-3 sentences) that the comment addresses
2. **Feedback**: Detailed, actionable feedback (2-4 sentences)
3. **Confidence**: high/medium/low
4. **Type**: error / gap / clarity / strength

Guidelines:
- Only flag genuine issues. If you resolve your own concern while reading, do NOT include it
- Cite specific claims, equations, tables, or assumptions
- For math-heavy sections, check derivations and proof logic
- For methodology, check: assumptions, identification, data quality, robustness
- For results, check: interpretation, significance, omitted analyses
- For discussion, check: whether claims are supported by results

Return as:
### Comment N
**Quote**: "..."
**Feedback**: ...
**Confidence**: high/medium/low
**Type**: error/gap/clarity/strength
""")
```

Launch all section tasks in parallel (up to 5-7 tasks simultaneously).

### Agent C: Cross-Section Consistency (if applicable)

If the paper has both RESULTS and DISCUSSION sections, launch one additional task:

```
task(category="deep", load_skills=[], run_in_background=true, prompt="""
You are checking whether the Discussion/Conclusion sections are consistent with the Results.

PAPER TITLE: <title>
RESULTS SECTION:
<results_text>
DISCUSSION/CONCLUSION SECTION:
<discussion_text>

Identify any claims in the Discussion that:
1. Are NOT supported by the Results
2. Overstate the findings
3. Ignore important caveats or limitations
4. Make causal claims without proper identification

Return 0-4 comments in the same format as section reviews.
""")
```

## Step 4: Collect Results

Wait for all background tasks to complete. For each task, read its output and extract:
- Overview issues
- Per-section comments
- Cross-section comments

Store all comments in a structured format.

## Step 5: Editorial Pass

Run a single editorial agent to filter the collected comments:

```
task(category="deep", load_skills=[], run_in_background=false, prompt="""
You are an editorial filter for peer review comments. Deduplicate, rank, and filter these comments.

PAPER TITLE: <title>
ABSTRACT: <abstract>

COLLECTED COMMENTS:
<all_comments>

Editorial rules:
1. **Remove duplicates**: If two comments address the same issue, keep the better one
2. **Remove contradictions**: If two comments contradict each other, flag both as low-confidence or remove
3. **Remove false positives**: Drop comments that state a concern and then answer it
4. **Remove generic praise**: Keep only substantive critical feedback
5. **Prioritize**: High-confidence, actionable comments first
6. **Ensure coverage**: Keep at least one comment per major section

Return the filtered list as:
### Comment N (renumbered)
**Quote**: "..."
**Feedback**: ...
**Confidence**: high/medium/low
**Type**: error/gap/clarity/strength
""")
```

## Step 6: Render Final Review

Write the final review to a markdown file in the current directory:

```markdown
# Peer Review: <Paper Title>

**Date**: MM/DD/YYYY
**Reviewer**: AI Peer Review (coarse-opencode)
**Format**: <original format>
**Domain**: <inferred domain>

---

## Overall Feedback

<overview issues from Agent A>

---

## Detailed Comments (N)

<all filtered and renumbered comments>

---

## Summary

<brief synthesis: main strengths and weaknesses>

**Recommendation**: <accept / minor revisions / major revisions / reject>
```

Save this to `paper_review.md` in the current working directory (or next to the input file).

## Step 7: Report to User

Show the user:
1. The output file path
2. Number of detailed comments
3. Top 2-3 macro issues
4. Recommendation
5. Any sections that had no comments (potential gaps in review coverage)

Example:
> Review complete! Output written to `/path/to/paper_review.md`
> 
> **Recommendation**: Major revisions
> **Comments**: 24 detailed comments
> 
> **Top issues**:
> 1. The identification strategy relies on an untestable exclusion restriction (Section 3)
> 2. Results overstate causal claims given the observational design (Section 5)
> 3. Missing robustness checks for the main specification (Section 4)

## Notes

- **No API keys needed**: All LLM calls go through your OpenCode subscription
- **For text/markdown inputs**: Zero external API calls. Everything runs through OpenCode
- **For PDF inputs**: Convert to text/markdown first. The skill will not process raw PDFs
- **Parallel execution**: Section reviews run in parallel via `task(run_in_background=true)`. A typical paper spawns 5-8 background tasks
- **Timeout**: Each review agent has a 10-minute timeout. If a section times out, the pipeline continues without that section's comments
- **Cost**: Uses your OpenCode subscription quota only. No per-paper charges
- **Reproducibility**: Results may vary between runs. For consistency, save the review output alongside the paper

## Troubleshooting

**"File too large"**: If the paper exceeds ~50 pages or 100KB, the section agents may time out. Split the paper into logical chunks or reduce the number of parallel tasks.

**"No sections found"**: The parser may fail on unusual formatting. Check that the paper has clear headings. You can manually specify section boundaries.

**"All comments dropped"**: The editorial filter may be too aggressive. Re-run with a note to the editorial agent to be less strict.

**PDF conversion**: Use `pdftotext input.pdf output.txt` (poppler-utils) or `python -m pdfplumber input.pdf > output.txt` for quick extraction.

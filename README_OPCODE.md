# coarse-opencode

**Coarse academic paper reviewer — OpenCode edition.**

This is a fork of [coarse](https://github.com/Davidvandijcke/coarse) adapted to work natively with [OpenCode](https://opencode.ai/), eliminating the need for OpenRouter API keys when reviewing text-based papers (markdown, text, LaTeX).

## What Changed

| Feature | Original coarse | This fork |
|---------|----------------|-----------|
| LLM backend | OpenRouter API (paid) | Your OpenCode subscription |
| Text extraction | Mistral OCR via OpenRouter | Native file reading (no API) |
| Required keys | `OPENROUTER_API_KEY` | None for text inputs |
| PDF support | Yes (OCR) | Convert to text first |
| Parallel agents | Python ThreadPool | OpenCode native `task()` |
| Cost per review | ~$0.25–$2.00 | Uses your OpenCode quota only |

## Prerequisites

- [OpenCode](https://opencode.ai/) installed and configured
- Python 3.10+ (for structure parsing helper)
- Git

## Quickstart

### 1. Clone this fork

```bash
git clone https://github.com/YOUR_USERNAME/coarse-opencode.git
cd coarse-opencode
```

### 2. Install the skill

**Option A: Symlink (recommended for development)**

```bash
# macOS/Linux
ln -s "$(pwd)/.opencode/skills/coarse-review" ~/.config/opencode/skills/coarse-review

# Windows (PowerShell, admin)
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.config\opencode\skills\coarse-review" -Target "$(pwd)\.opencode\skills\coarse-review"
```

**Option B: Copy (recommended for stable use)**

```bash
# macOS/Linux
cp -r .opencode/skills/coarse-review ~/.config/opencode/skills/

# Windows
xcopy /E /I .opencode\skills\coarse-review %USERPROFILE%\.config\opencode\skills\coarse-review
```

### 3. Use the skill

In any OpenCode session, invoke:

```
/coarse-review path/to/paper.md
```

Or without arguments (it will ask for the path):

```
/coarse-review
```

## Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Markdown | `.md`, `.markdown` | Best format, full support |
| Plain text | `.txt` | Full support |
| LaTeX | `.tex` | Full support |
| DOCX | `.docx` | Supported via python-docx |
| HTML | `.html` | Supported |
| EPUB | `.epub` | Supported |
| PDF | `.pdf` | **Not directly supported** — convert first |

## Converting PDFs

If you have a PDF, convert it to markdown or text before reviewing:

### Option 1: pdftotext (fastest)

```bash
# macOS
brew install poppler
pdftotext paper.pdf paper.txt

# Ubuntu/Debian
sudo apt-get install poppler-utils
pdftotext paper.pdf paper.txt
```

### Option 2: Python (better formatting)

```bash
pip install pdfplumber
python3 -c "import pdfplumber; pdfplumber.open('paper.pdf').pages[0].extract_text()" > paper.txt
```

### Option 3: MarkItDown (best for academic papers)

```bash
pip install markitdown
markitdown paper.pdf > paper.md
```

### Option 4: Use the split-pdf skill

If you have the `split-pdf` OpenCode skill installed:

```
/split-pdf paper.pdf
```

This will create a structured markdown extraction.

## How It Works

The OpenCode skill implements the same review pipeline as the original coarse:

1. **Load & Parse** — Read the file, split into sections using regex
2. **Structure Analysis** — Identify title, abstract, sections, domain
3. **Parallel Review Agents** — Launch background tasks for:
   - Overview review (macro issues)
   - Per-section reviews (detailed comments)
   - Cross-section consistency check
4. **Editorial Pass** — Filter duplicates, contradictions, low-quality comments
5. **Output** — Render final markdown review

All LLM calls go through your OpenCode subscription. No external API keys needed.

## Pipeline Details

### Phase 1: Structure Analysis

The skill parses the paper using a Python helper script that:
- Extracts the title (first heading or first line)
- Extracts the abstract (text under "Abstract" heading)
- Splits into sections by markdown headings (`#`, `##`, `###`)
- Classifies each section type (Introduction, Methods, Results, etc.)
- Detects math content (LaTeX equations)

### Phase 2: Parallel Review

Launches 5-8 background tasks simultaneously:
- **1 overview agent** — 4-6 macro issues
- **4-6 section agents** — 3-8 detailed comments per section
- **1 cross-section agent** — Results vs. discussion consistency (if applicable)

Each agent receives the full paper text plus section-specific instructions.

### Phase 3: Editorial Filter

A single agent reviews all collected comments and:
- Removes duplicates
- Drops contradictions
- Eliminates false positives
- Ranks by confidence and actionability
- Ensures coverage across all major sections

### Phase 4: Output

Renders a structured markdown review:

```markdown
# Peer Review: Paper Title

**Date**: 01/15/2026
**Reviewer**: AI Peer Review (coarse-opencode)
**Format**: markdown

---

## Overall Feedback

### Issue 1: ...
...

---

## Detailed Comments (24)

### Comment 1
**Quote**: "..."
**Feedback**: ...
**Confidence**: high
**Type**: gap

---

## Summary

...

**Recommendation**: major revisions
```

## Comparison with Original coarse

| Aspect | Original | This fork |
|--------|----------|-----------|
| **Extraction** | Mistral OCR + Docling | Native file read |
| **Structure analysis** | LLM-based | Regex + heuristics |
| **Literature search** | Perplexity Sonar Pro | Not included |
| **Quote verification** | Fuzzy matching | Manual (agent-based) |
| **Proof verification** | Adversarial LLM | Standard review |
| **Cost** | $0.25–$2/paper | OpenCode quota only |
| **Speed** | 10-25 min | 5-15 min |
| **Setup** | API keys + install | Just the skill |

**Trade-offs**: This fork is simpler and free but lacks the original's automated literature search, programmatic quote verification, and adversarial proof checking. For most users reviewing text-based papers, the quality difference is minimal.

## Configuration

No configuration needed. The skill uses OpenCode's default model settings.

If you want to use a specific model for reviews, you can set it in your OpenCode config:

```bash
# ~/.config/opencode/config.toml
[model]
default = "claude-sonnet-4"  # or your preferred model
```

## Troubleshooting

### "File too large"

If the paper exceeds ~50 pages, section agents may time out. Solutions:
- Split the paper into logical chunks
- Reduce the number of parallel tasks
- Use a faster model

### "No sections found"

The parser expects clear headings. If your paper uses unusual formatting:
- Add markdown headings manually
- Or use a different conversion tool

### "PDF not supported"

This is by design. Convert PDFs to text/markdown first. See [Converting PDFs](#converting-pdfs).

### Skill not found

Ensure the skill is in the right location:

```bash
ls ~/.config/opencode/skills/coarse-review/SKILL.md
```

If missing, re-run the installation step.

## Development

To modify the skill:

1. Edit `.opencode/skills/coarse-review/SKILL.md`
2. Test with a sample paper
3. The changes are live immediately (no restart needed for symlinked skills)

### Adding new features

The skill is a markdown file with OpenCode tool instructions. You can extend it by:
- Adding new agent prompts in the parallel review section
- Modifying the editorial filter rules
- Changing the output format
- Adding domain-specific review criteria

## Contributing

This fork welcomes contributions:
- Better parsing for unusual formats
- Additional language support
- Improved prompts
- Bug fixes

Please open an issue or PR on this fork's repository.

## Credits

- Original [coarse](https://github.com/Davidvandijcke/coarse) by David van Dijcke
- OpenCode adaptation by Arthur Zampieri

## License

MIT (same as original coarse)

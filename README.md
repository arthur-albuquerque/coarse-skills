# coarse-review

> **Zero API keys. Zero setup. Just your coding agent subscription.**
>
> Review academic papers using the Claude Code or OpenCode subscription you already have. No OpenRouter. No Anthropic API. No Perplexity. No Python package to install.

A skill for Claude Code and OpenCode that produces rigorous academic peer reviews. Feed it a paper, get a structured markdown review back.

## What Is This?

This is a lightweight fork of [coarse](https://github.com/Davidvandijcke/coarse), a web-based academic paper review tool by David van Dijcke. The original tool requires OpenRouter API keys, a Python package install (`pip install coarse`), and a web backend (Supabase, Modal workers, subscription management).

**This fork reimplements the same peer review logic as a native skill** for Claude Code and OpenCode, leveraging your existing agent subscription instead of external APIs. It replaces the original's 11,000-line Python package and web infrastructure with ~600 lines of bundled scripts plus native agent parallelization.

## Quick Start

### Option 1: Run from this repo (no install)

```bash
# Clone or navigate to this repo
cd coarse-opencode

# The skill is auto-discovered when you're in the repo
/coarse-review ~/papers/diffusion_models.md
```

### Option 2: Install globally

```bash
./install.sh
```

This symlinks the skill into:
- `~/.claude/skills/coarse-review` (Claude Code)
- `~/.config/opencode/skills/coarse-review` (OpenCode)

Then use it from anywhere:
```bash
/coarse-review ~/papers/diffusion_models.md
```

## What You Need

| | Claude Code | OpenCode |
|---|---|---|
| **Subscription** | Claude Code | OpenCode |
| **Paper formats** | `.md` `.txt` `.tex` `.docx` `.html` `.epub` | same |
| **PDFs?** | Convert to text first (`pdftotext`, `pdfplumber`) | same |
| **API keys** | None | None |
| **Python** | 3.x (for bundled scripts) | 3.x (for bundled scripts) |

## How It Works

The skill bundles three Python scripts that handle deterministic work, leaving the LLM reasoning to your agent subscription:

1. **Parse** (`scripts/parse_paper.py`) — Split paper into sections, extract claims/definitions, detect math content, classify document form
2. **Verify** (`scripts/verify_quotes.py`) — Confirm every comment quote is an actual substring of the paper (catches hallucinations)
3. **Extract** (`scripts/extract_text.py`) — Convert `.docx`, `.html`, `.epub`, `.tex` to markdown

Then the skill spawns parallel review agents:
4. **Overview** — High-level macro issues (conceptual gaps, methodological concerns)
5. **Per-section** — Detailed comments per major section (3-8 comments each)
6. **Cross-section** — Consistency check between Results and Discussion
7. **Editorial** — Filter duplicates, rank by severity
8. **Output** — Structured markdown review (`paper_review.md`)

## Example

```bash
/coarse-review ~/papers/diffusion_models.md
# → writes paper_review.md in current directory
```

Output:
- **Overall Feedback**: 4-6 high-level issues
- **Detailed Comments**: 15-30 specific, quoted comments with confidence levels
- **Quote Verification**: Exact matches, fuzzy-corrected quotes, dropped hallucinations
- **Recommendation**: accept / minor revisions / major revisions / reject

## Project Structure

```
coarse-opencode/
├── .claude/
│   └── skills/
│       └── coarse-review/
│           ├── SKILL.md              # Claude skill instructions
│           └── scripts/
│               ├── parse_paper.py    # Structure parsing
│               ├── verify_quotes.py  # Quote verification
│               └── extract_text.py   # Format conversion
├── .opencode/
│   └── skills/
│       └── coarse-review/            # Same structure for OpenCode
├── install.sh                        # Global installer
├── LICENSE
└── README.md
```

## Install

### Both platforms at once

```bash
./install.sh
```

### Claude Code only

```bash
ln -s "$(pwd)/.claude/skills/coarse-review" ~/.claude/skills/coarse-review
# or
cp -r .claude/skills/coarse-review ~/.claude/skills/
```

### OpenCode only

```bash
ln -s "$(pwd)/.opencode/skills/coarse-review" ~/.config/opencode/skills/coarse-review
# or
./install.sh
```

## Uninstall

```bash
rm -rf ~/.claude/skills/coarse-review
rm -rf ~/.config/opencode/skills/coarse-review
```

## Comparison: This Fork vs. Original coarse

This fork strips away the original's web backend, worker queues, and API infrastructure, replacing them with native agent parallelization. Here's the difference:

| | Original coarse | This skill |
|---|---|---|
| **LLM backend** | OpenRouter API (~$0.25-2.00/review) | Your existing agent subscription |
| **Required keys** | `OPENROUTER_API_KEY` | None |
| **Setup** | 5-10 min | 1 min (OpenCode) / 0 min (Claude Code) |
| **Python package** | 11,000 lines | 3 scripts, ~600 lines |
| **Quote verification** | Yes (Python) | Yes (bundled script) |
| **Parallelism** | Python ThreadPool | Native agent fan-out |

The original `coarse` runs reviews through a web backend with Python ThreadPool workers and OpenRouter API calls. This fork runs reviews through your agent's native parallel subagents, and the bundled scripts handle all deterministic work (parsing, verification, extraction) without any API calls.

## Credits

- **Original tool**: [coarse](https://github.com/Davidvandijcke/coarse) by David van Dijcke — the web-based review system this fork reimplements
- **This fork**: Native skill adaptations for Claude Code and OpenCode by the OpenCode community

MIT License (same as original)

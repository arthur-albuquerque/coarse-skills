# coarse-opencode

**OpenCode-native academic paper reviewer** — a fork of [coarse](https://github.com/Davidvandijcke/coarse) that uses your OpenCode subscription instead of OpenRouter API keys.

## Quick Start

```bash
# 1. Clone this fork
git clone https://github.com/YOUR_USERNAME/coarse-opencode.git
cd coarse-opencode

# 2. Install the skill
./install.sh

# 3. Use it in OpenCode
/coarse-review path/to/paper.md
```

## What Changed

| Feature | Original coarse | This fork |
|---------|----------------|-----------|
| LLM backend | OpenRouter API (paid per review) | Your OpenCode subscription |
| Text extraction | Mistral OCR via OpenRouter | Native file reading (no API) |
| Required keys | `OPENROUTER_API_KEY` | None for text inputs |
| PDF support | Yes (with OCR) | Convert to text first |
| Parallel agents | Python ThreadPool | OpenCode native `task()` |
| Cost per review | ~$0.25–$2.00 | OpenCode quota only |
| Setup time | 5-10 min (API keys, config) | 1 min (just install skill) |

## Documentation

- **[Full README](README_OPCODE.md)** — Detailed usage, configuration, troubleshooting
- **[Skill File](.opencode/skills/coarse-review/SKILL.md)** — The OpenCode skill implementation
- **[Parser Script](scripts/parse_paper.py)** — Structure parsing helper

## Supported Formats

- ✅ `.md` / `.markdown` — Best format, full support
- ✅ `.txt` — Plain text, full support  
- ✅ `.tex` — LaTeX source, full support
- ✅ `.docx` — DOCX via python-docx
- ✅ `.html` / `.epub` — Supported
- ⚠️ `.pdf` — Convert to text first (see README_OPCODE.md)

## How It Works

The OpenCode skill implements the same review pipeline as the original coarse:

1. **Load & Parse** — Read file, split into sections
2. **Structure Analysis** — Identify title, abstract, sections, domain
3. **Parallel Review Agents** — Launch background tasks for:
   - Overview review (macro issues)
   - Per-section reviews (detailed comments)
   - Cross-section consistency check
4. **Editorial Pass** — Filter duplicates, contradictions, low-quality comments
5. **Output** — Render structured markdown review

All LLM calls go through your OpenCode subscription. No external API keys.

## Requirements

- [OpenCode](https://opencode.ai/) installed and configured
- Python 3.10+ (for structure parsing helper)
- For PDF inputs: `pdftotext` or similar conversion tool

## Install

```bash
./install.sh
```

This symlinks the skill to `~/.config/opencode/skills/coarse-review`.

## Uninstall

```bash
rm -rf ~/.config/opencode/skills/coarse-review
```

## Example Output

```markdown
# Peer Review: The Impact of Minimum Wage on Employment: A Meta-Analysis

**Date**: 05/13/2026
**Reviewer**: AI Peer Review (coarse-opencode)
**Format**: markdown

---

## Overall Feedback

### Issue 1: Identification strategy relies on untestable exclusion restriction
The paper assumes that the exclusion restriction holds for all instruments, but...

### Issue 2: Results overstate causal claims
The observational design limits causal interpretation, yet the Discussion...

---

## Detailed Comments (24)

### Comment 1
**Quote**: "We find a small but statistically significant negative effect on employment (-0.08, 95% CI: -0.12 to -0.04)"
**Feedback**: While the point estimate is precise, the practical significance of a 0.08 standard deviation effect is questionable. The authors should discuss the economic magnitude more explicitly and compare it to meaningful benchmarks (e.g., typical employment elasticities in the literature).
**Confidence**: medium
**Type**: clarity

---

## Summary

This paper makes a valuable contribution by synthesizing 45 studies on minimum wage effects. The meta-analytic methods are generally sound, and the heterogeneity analysis is particularly insightful. However, the paper would benefit from more careful causal language, additional robustness checks, and a clearer discussion of economic magnitudes.

**Recommendation**: major revisions
```

## Development

To modify the skill, edit `.opencode/skills/coarse-review/SKILL.md`.

To test changes, run:
```bash
python3 scripts/parse_paper.py tests/sample_paper.md | jq '.sections | length'
```

## Contributing

This fork welcomes:
- Better parsing for unusual formats
- Additional language support
- Improved prompts
- Bug fixes

Please open an issue or PR.

## Credits

- Original [coarse](https://github.com/Davidvandijcke/coarse) by David van Dijcke
- OpenCode adaptation by community contributors

## License

MIT (same as original coarse)

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== coarse-review Skill Installer ==="
echo ""
echo "This will install the coarse-review skill for:"
echo "  1. Claude Code  (~/.claude/skills/)"
echo "  2. OpenCode     (~/.config/opencode/skills/)"
echo ""

CLAUDE_SKILL_SOURCE="$SCRIPT_DIR/.claude/skills/coarse-review"
CLAUDE_SKILL_TARGET="${HOME}/.claude/skills/coarse-review"

if [ -e "$CLAUDE_SKILL_TARGET" ]; then
    echo "Claude Code skill already exists at: $CLAUDE_SKILL_TARGET"
    read -p "Replace existing Claude Code skill? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$CLAUDE_SKILL_TARGET"
        cp -r "$CLAUDE_SKILL_SOURCE" "$CLAUDE_SKILL_TARGET"
        echo "✓ Claude Code skill installed"
    else
        echo "  Skipped Claude Code installation"
    fi
else
    mkdir -p "${HOME}/.claude/skills"
    cp -r "$CLAUDE_SKILL_SOURCE" "$CLAUDE_SKILL_TARGET"
    echo "✓ Claude Code skill installed"
fi

echo ""

OPENCODE_SKILL_SOURCE="$SCRIPT_DIR/.opencode/skills/coarse-review"
OPENCODE_SKILL_TARGET="${HOME}/.config/opencode/skills/coarse-review"

if [ -e "$OPENCODE_SKILL_TARGET" ]; then
    echo "OpenCode skill already exists at: $OPENCODE_SKILL_TARGET"
    read -p "Replace existing OpenCode skill? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$OPENCODE_SKILL_TARGET"
        cp -r "$OPENCODE_SKILL_SOURCE" "$OPENCODE_SKILL_TARGET"
        echo "✓ OpenCode skill installed"
    else
        echo "  Skipped OpenCode installation"
    fi
else
    mkdir -p "${HOME}/.config/opencode/skills"
    cp -r "$OPENCODE_SKILL_SOURCE" "$OPENCODE_SKILL_TARGET"
    echo "✓ OpenCode skill installed"
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Usage:"
echo "  Claude Code:  /coarse-review path/to/paper.md"
echo "  OpenCode:     /coarse-review path/to/paper.md"
echo ""
echo "To uninstall:"
echo "  rm -rf ~/.claude/skills/coarse-review"
echo "  rm -rf ~/.config/opencode/skills/coarse-review"

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SOURCE="$SCRIPT_DIR/.opencode/skills/coarse-review"
SKILL_TARGET="${HOME}/.config/opencode/skills/coarse-review"

echo "=== coarse-opencode Skill Installer ==="
echo ""

if [ ! -d "${HOME}/.config/opencode/skills" ]; then
    echo "Creating OpenCode skills directory..."
    mkdir -p "${HOME}/.config/opencode/skills"
fi

if [ -e "$SKILL_TARGET" ]; then
    echo "Skill already exists at: $SKILL_TARGET"
    read -p "Replace existing skill? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    rm -rf "$SKILL_TARGET"
fi

echo "Installing skill from: $SKILL_SOURCE"
echo "Installing to: $SKILL_TARGET"

if command -v ln &> /dev/null && [ ! "${FORCE_COPY:-}" = "true" ]; then
    ln -s "$SKILL_SOURCE" "$SKILL_TARGET"
    echo "Installed as symlink (changes to skill are reflected immediately)"
else
    cp -r "$SKILL_SOURCE" "$SKILL_TARGET"
    echo "Installed as copy (stable, requires re-install for updates)"
fi

echo ""
echo "✓ Skill installed successfully!"
echo ""
echo "Usage:"
echo "  /coarse-review path/to/paper.md"
echo ""
echo "For PDF inputs, convert first:"
echo "  pdftotext paper.pdf paper.txt"
echo "  # or"
echo "  python3 scripts/parse_paper.py paper.docx > paper_structure.json"
echo ""
echo "To uninstall:"
echo "  rm -rf $SKILL_TARGET"

#!/usr/bin/env python3
"""Parse academic paper structure from markdown/text.

Helper script for the coarse-opencode skill. Reads a paper file,
extracts title/abstract/sections, and outputs JSON for downstream review.

Usage:
    python3 parse_paper.py paper.md > structure.json
    python3 parse_paper.py paper.txt > structure.json
    python3 parse_paper.py paper.tex > structure.json

Supports: .md, .txt, .tex, .docx, .html, .epub
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def extract_text_from_docx(path: Path) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        import docx
    except ImportError:
        raise ImportError("python-docx not installed. Run: pip install python-docx")
    
    doc = docx.Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_html(path: Path) -> str:
    """Extract text from HTML using html.parser."""
    from html.parser import HTMLParser

    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text_parts: list[str] = []
            self.in_script = False

        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style"):
                self.in_script = True
            if tag in ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"):
                self.text_parts.append("\n")

        def handle_endtag(self, tag):
            if tag in ("script", "style"):
                self.in_script = False
            if tag in ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"):
                self.text_parts.append("\n")

        def handle_data(self, data):
            if not self.in_script:
                self.text_parts.append(data)

    extractor = TextExtractor()
    extractor.feed(path.read_text(encoding="utf-8"))
    return re.sub(r"\n+", "\n", "".join(extractor.text_parts)).strip()


def extract_text_from_epub(path: Path) -> str:
    """Extract text from EPUB using ebooklib."""
    try:
        import ebooklib
        from ebooklib import epub
    except ImportError:
        raise ImportError("ebooklib not installed. Run: pip install EbookLib")

    book = epub.read_epub(str(path))
    texts: list[str] = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            texts.append(extract_text_from_html_content(item.get_content().decode("utf-8")))
    return "\n\n".join(texts)


def extract_text_from_html_content(html: str) -> str:
    """Extract text from HTML string."""
    from html.parser import HTMLParser

    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text_parts: list[str] = []
            self.in_script = False

        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style"):
                self.in_script = True
            if tag in ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "br"):
                self.text_parts.append("\n")

        def handle_endtag(self, tag):
            if tag in ("script", "style"):
                self.in_script = False

        def handle_data(self, data):
            if not self.in_script:
                self.text_parts.append(data)

    extractor = TextExtractor()
    extractor.feed(html)
    return re.sub(r"\n+", "\n", "".join(extractor.text_parts)).strip()


def read_paper(path: Path) -> str:
    """Read paper text from any supported format."""
    ext = path.suffix.lower()
    
    if ext in (".md", ".txt", ".markdown"):
        return path.read_text(encoding="utf-8")
    
    if ext == ".tex":
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(?<!\\)%.*?\n", "\n", text)
        text = re.sub(r"\\section\*?\{([^}]+)\}", r"# \1", text)
        text = re.sub(r"\\subsection\*?\{([^}]+)\}", r"## \1", text)
        text = re.sub(r"\\subsubsection\*?\{([^}]+)\}", r"### \1", text)
        text = re.sub(r"\\[a-zA-Z]+\*?(\{[^}]*\})*(\[[^\]]*\])*", "", text)
        text = re.sub(r"[{}]", "", text)
        return text
    
    if ext == ".docx":
        return extract_text_from_docx(path)
    
    if ext in (".html", ".htm"):
        return extract_text_from_html(path)
    
    if ext == ".epub":
        return extract_text_from_epub(path)
    
    raise ValueError(f"Unsupported format: {ext}")


def parse_structure(text: str) -> dict[str, Any]:
    """Parse paper structure from text."""
    lines = text.split("\n")
    title = "Untitled"
    for line in lines[:20]:
        stripped = line.strip()
        if stripped.startswith("# ") and len(stripped) > 3:
            title = stripped[2:].strip()
            break
        elif stripped and not stripped.startswith("#") and len(stripped) > 10:
            title = stripped
            break
    abstract = ""
    in_abstract = False
    for i, line in enumerate(lines):
        if re.match(r"^#*\s*abstract", line.strip(), re.IGNORECASE):
            in_abstract = True
            continue
        if in_abstract:
            if re.match(r"^#{1,4}\s", line):
                break
            abstract += line + "\n"
    abstract = abstract.strip()
    sections: list[dict[str, Any]] = []
    current_title = ""
    current_text: list[str] = []
    current_level = 0
    
    for line in lines:
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m:
            if current_title:
                sections.append({
                    "title": current_title,
                    "level": current_level,
                    "text": "\n".join(current_text).strip(),
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
            "text": "\n".join(current_text).strip(),
        })
    if not sections:
        sections.append({
            "title": "Main Text",
            "level": 1,
            "text": text.strip(),
        })
    type_map: dict[str, str] = {
        "abstract": "ABSTRACT",
        "introduction": "INTRODUCTION",
        "related work": "RELATED_WORK",
        "literature": "RELATED_WORK",
        "prior work": "RELATED_WORK",
        "background": "RELATED_WORK",
        "method": "METHODOLOGY",
        "methods": "METHODOLOGY",
        "methodology": "METHODOLOGY",
        "approach": "METHODOLOGY",
        "model": "METHODOLOGY",
        "models": "METHODOLOGY",
        "identification": "METHODOLOGY",
        "estimation": "METHODOLOGY",
        "result": "RESULTS",
        "results": "RESULTS",
        "finding": "RESULTS",
        "findings": "RESULTS",
        "experiment": "RESULTS",
        "experiments": "RESULTS",
        "simulation": "RESULTS",
        "empirical": "RESULTS",
        "discussion": "DISCUSSION",
        "conclusion": "CONCLUSION",
        "conclusions": "CONCLUSION",
        "concluding": "CONCLUSION",
        "summary": "CONCLUSION",
        "appendix": "APPENDIX",
        "appendices": "APPENDIX",
        "supplementary": "APPENDIX",
        "reference": "REFERENCES",
        "references": "REFERENCES",
        "bibliography": "REFERENCES",
    }
    
    for sec in sections:
        sec_title_lower = sec["title"].lower()
        sec["type"] = "OTHER"
        for keyword, stype in type_map.items():
            if keyword in sec_title_lower:
                sec["type"] = stype
                break
        math_markers = ["$", r"\[", r"\begin{equation", r"\begin{align"]
        sec["math"] = any(m in sec["text"] for m in math_markers)
    
    return {
        "title": title,
        "abstract": abstract,
        "sections": sections,
        "total_chars": len(text),
        "total_sections": len(sections),
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 parse_paper.py <paper-file>", file=sys.stderr)
        sys.exit(1)
    
    path = Path(sys.argv[1]).expanduser()
    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        text = read_paper(path)
        structure = parse_structure(text)
        print(json.dumps(structure, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

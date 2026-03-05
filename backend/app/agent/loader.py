"""
Skill loader: reads *.md files from a directory and returns MarkdownSkill instances.

Each .md file must begin with a YAML frontmatter block (between --- delimiters)
that declares at minimum `name` and `description`. An optional `flags` mapping
controls what metadata is attached to the SkillResult (e.g. suggest_meditation).

The body of the file is split into named sections by ## headings.
The content of the `## 回應` section becomes the exact message returned to the
user when the skill is triggered. All other sections are documentation only.

Example file structure:
    ---
    name: suggest_meditation
    description: 當使用者焦慮時呼叫此技能。
    flags:
      suggest_meditation: true
    ---

    # 引導呼吸練習

    [overall instructions]

    ## 回應
    具體回應給使用者的文字內容。

    ## 適用情境
    - Example 1

    ## 執行準則
    - Guideline 1
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.agent.base import SkillBase, SkillResult

# The section heading that contains the message returned to the user.
_RESPONSE_SECTION = "回應"


class MarkdownSkill(SkillBase):
    """A skill whose definition lives entirely in a .md file."""

    def __init__(
        self,
        name: str,
        description: str,
        message: str,
        flags: Dict[str, Any],
    ) -> None:
        self.name = name
        self.description = description
        self._message = message
        self._flags = flags

    def execute(self, args: Dict[str, Any]) -> SkillResult:
        return SkillResult(message=self._message, flags=self._flags)


# ------------------------------------------------------------------ #
# Parsing helpers                                                      #
# ------------------------------------------------------------------ #

def _parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Split a .md file into (frontmatter_dict, body_str).

    Handles the simple YAML subset used by skill files:
      - scalar key: value pairs
      - one level of nested mapping for `flags:`
      - boolean values true/false
    Returns ({}, content) if no valid frontmatter block is found.
    """
    if not content.startswith("---"):
        return {}, content

    # Find the closing delimiter (skip the opening one at pos 0)
    close = content.find("\n---", 3)
    if close == -1:
        return {}, content

    fm_text = content[3:close].strip()
    body = content[close + 4:].strip()
    return _parse_simple_yaml(fm_text), body


def _parse_simple_yaml(text: str) -> Dict[str, Any]:
    """Parse a minimal YAML subset (scalars + one-level nested mappings)."""
    result: Dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in text.splitlines():
        # Detect indentation level
        stripped = raw_line.lstrip()
        indent = len(raw_line) - len(stripped)

        if not stripped or stripped.startswith("#"):
            continue

        if ":" not in stripped:
            continue

        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip()

        if indent > 0 and current_key is not None:
            # Nested value under current_key
            if not isinstance(result.get(current_key), dict):
                result[current_key] = {}
            result[current_key][key] = _coerce(val)
        else:
            # Top-level key
            current_key = key
            result[key] = _coerce(val) if val else {}

    return result


def _coerce(value: str) -> Any:
    """Convert YAML scalar strings to Python types."""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def _extract_section(body: str, heading: str) -> str:
    """Return the text under a `## heading` section (stripped).

    Falls back to the full body if the section is not found.
    """
    pattern = rf"##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##\s|\Z)"
    match = re.search(pattern, body, re.DOTALL)
    if match:
        return match.group(1).strip()
    return body.strip()


# ------------------------------------------------------------------ #
# Public API                                                           #
# ------------------------------------------------------------------ #

def load_skill_from_file(path: Path) -> MarkdownSkill:
    """Parse a single .md skill file and return a MarkdownSkill instance."""
    content = path.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(content)

    name: str = frontmatter.get("name", path.stem)
    description: str = frontmatter.get("description", "")
    flags: Dict[str, Any] = frontmatter.get("flags", {})
    message: str = _extract_section(body, _RESPONSE_SECTION)

    return MarkdownSkill(name=name, description=description, message=message, flags=flags)


def load_skills_from_dir(directory: Path) -> List[MarkdownSkill]:
    """Load all *.md files in *directory* and return a list of MarkdownSkill instances.

    Files are loaded in alphabetical order so the registry order is deterministic.
    """
    return [
        load_skill_from_file(md_file)
        for md_file in sorted(directory.glob("*.md"))
    ]

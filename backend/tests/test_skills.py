"""
Tests for the skills-based agent architecture.
Covers: SkillResult, loader (frontmatter parser + section extractor),
        MarkdownSkill, SkillRegistry, and the shared .md-backed singleton.
"""
import textwrap
from pathlib import Path

import pytest

from app.agent.base import SkillBase, SkillResult
from app.agent.loader import (
    MarkdownSkill,
    _coerce,
    _extract_section,
    _parse_frontmatter,
    _parse_simple_yaml,
    load_skill_from_file,
    load_skills_from_dir,
)
from app.agent.registry import SkillRegistry


# ------------------------------------------------------------------ #
# SkillResult                                                          #
# ------------------------------------------------------------------ #

def test_skill_result_defaults():
    result = SkillResult(message="hello")
    assert result.message == "hello"
    assert result.flags == {}
    assert result.flags.get("suggest_meditation", False) is False


def test_skill_result_with_flags():
    result = SkillResult(message="test", flags={"suggest_meditation": True})
    assert result.flags["suggest_meditation"] is True


# ------------------------------------------------------------------ #
# Frontmatter parser helpers                                           #
# ------------------------------------------------------------------ #

def test_coerce_bool_true():
    assert _coerce("true") is True
    assert _coerce("True") is True


def test_coerce_bool_false():
    assert _coerce("false") is False


def test_coerce_int():
    assert _coerce("42") == 42


def test_coerce_float():
    assert _coerce("3.14") == pytest.approx(3.14)


def test_coerce_string():
    assert _coerce("hello") == "hello"


def test_parse_simple_yaml_scalars():
    text = "name: suggest_meditation\ndescription: Some skill"
    result = _parse_simple_yaml(text)
    assert result["name"] == "suggest_meditation"
    assert result["description"] == "Some skill"


def test_parse_simple_yaml_nested_flags():
    text = "name: foo\nflags:\n  suggest_meditation: true\n  play_audio: false"
    result = _parse_simple_yaml(text)
    assert result["flags"]["suggest_meditation"] is True
    assert result["flags"]["play_audio"] is False


def test_parse_frontmatter_valid():
    content = textwrap.dedent("""\
        ---
        name: test_skill
        description: A test skill
        flags:
          suggest_meditation: true
        ---

        # Title

        Some body text.
    """)
    fm, body = _parse_frontmatter(content)
    assert fm["name"] == "test_skill"
    assert fm["flags"]["suggest_meditation"] is True
    assert "Title" in body


def test_parse_frontmatter_no_block():
    content = "Just a plain body with no frontmatter."
    fm, body = _parse_frontmatter(content)
    assert fm == {}
    assert body == content


def test_extract_section_found():
    body = "## 回應\nThis is the response.\n## 適用情境\nSome context."
    result = _extract_section(body, "回應")
    assert result == "This is the response."


def test_extract_section_multiline():
    body = "## 回應\nLine one.\nLine two.\n## 其他\nOther."
    result = _extract_section(body, "回應")
    assert "Line one." in result
    assert "Line two." in result


def test_extract_section_missing_falls_back_to_body():
    body = "No sections here at all."
    result = _extract_section(body, "回應")
    assert result == body.strip()


# ------------------------------------------------------------------ #
# load_skill_from_file                                                 #
# ------------------------------------------------------------------ #

def test_load_skill_from_file_meditation(tmp_path):
    md = tmp_path / "test_med.md"
    md.write_text(textwrap.dedent("""\
        ---
        name: suggest_meditation
        description: 測試冥想技能
        flags:
          suggest_meditation: true
        ---

        # 冥想

        ## 回應
        放鬆一下吧。

        ## 適用情境
        - 焦慮時
    """), encoding="utf-8")

    skill = load_skill_from_file(md)
    assert isinstance(skill, MarkdownSkill)
    assert skill.name == "suggest_meditation"
    assert skill.description == "測試冥想技能"
    result = skill.execute({})
    assert result.message == "放鬆一下吧。"
    assert result.flags["suggest_meditation"] is True


def test_load_skill_from_file_no_meditation_flag(tmp_path):
    md = tmp_path / "grounding.md"
    md.write_text(textwrap.dedent("""\
        ---
        name: suggest_grounding
        description: 著陸練習
        flags:
          suggest_meditation: false
        ---

        ## 回應
        回到當下。
    """), encoding="utf-8")

    skill = load_skill_from_file(md)
    result = skill.execute({})
    assert result.flags.get("suggest_meditation") is False


# ------------------------------------------------------------------ #
# load_skills_from_dir                                                 #
# ------------------------------------------------------------------ #

def test_load_skills_from_dir(tmp_path):
    for name, flag in [("alpha", True), ("beta", False)]:
        (tmp_path / f"{name}.md").write_text(textwrap.dedent(f"""\
            ---
            name: {name}_skill
            description: {name} desc
            flags:
              suggest_meditation: {str(flag).lower()}
            ---

            ## 回應
            {name} response.
        """), encoding="utf-8")

    skills = load_skills_from_dir(tmp_path)
    assert len(skills) == 2
    # alphabetical order: alpha, beta
    assert skills[0].name == "alpha_skill"
    assert skills[1].name == "beta_skill"


def test_load_skills_from_dir_empty(tmp_path):
    assert load_skills_from_dir(tmp_path) == []


# ------------------------------------------------------------------ #
# MarkdownSkill.get_definition                                         #
# ------------------------------------------------------------------ #

def test_markdown_skill_definition():
    skill = MarkdownSkill(
        name="test_skill",
        description="A description",
        message="A message",
        flags={},
    )
    defn = skill.get_definition()
    assert defn["name"] == "test_skill"
    assert defn["description"] == "A description"
    assert defn["input_schema"]["type"] == "object"


# ------------------------------------------------------------------ #
# SkillRegistry with MarkdownSkill instances                           #
# ------------------------------------------------------------------ #

@pytest.fixture
def registry(tmp_path):
    """Registry pre-loaded with two MarkdownSkills."""
    r = SkillRegistry()
    r.register_instance(MarkdownSkill("skill_a", "desc a", "msg a", {"suggest_meditation": True}))
    r.register_instance(MarkdownSkill("skill_b", "desc b", "msg b", {"suggest_meditation": False}))
    return r


def test_registry_has_registered_skills(registry):
    assert registry.has_skill("skill_a")
    assert registry.has_skill("skill_b")


def test_registry_get_definitions_count(registry):
    assert len(registry.get_definitions()) == 2


def test_registry_definitions_have_required_keys(registry):
    for defn in registry.get_definitions():
        assert "name" in defn
        assert "description" in defn
        assert "input_schema" in defn


def test_registry_execute_sets_flag(registry):
    result = registry.execute("skill_a", {})
    assert result.flags.get("suggest_meditation") is True


def test_registry_execute_unsets_flag(registry):
    result = registry.execute("skill_b", {})
    assert result.flags.get("suggest_meditation") is False


def test_registry_execute_unknown_returns_skill_result(registry):
    result = registry.execute("nonexistent", {})
    assert isinstance(result, SkillResult)
    assert not result.flags.get("suggest_meditation", False)


def test_registry_register_instance_replaces_duplicate(registry):
    registry.register_instance(MarkdownSkill("skill_a", "new desc", "new msg", {}))
    defs = [d for d in registry.get_definitions() if d["name"] == "skill_a"]
    assert len(defs) == 1
    assert defs[0]["description"] == "new desc"


# ------------------------------------------------------------------ #
# Shared .md-backed singleton (integration test)                       #
# ------------------------------------------------------------------ #

def test_shared_registry_loads_all_md_skills():
    from app.agent.skills import skill_registry
    assert skill_registry.has_skill("suggest_meditation")
    assert skill_registry.has_skill("suggest_grounding")
    assert skill_registry.has_skill("give_affirmation")


def test_shared_registry_meditation_sets_flag():
    from app.agent.skills import skill_registry
    result = skill_registry.execute("suggest_meditation", {})
    assert result.flags.get("suggest_meditation") is True


def test_shared_registry_grounding_does_not_set_flag():
    from app.agent.skills import skill_registry
    result = skill_registry.execute("suggest_grounding", {})
    assert result.flags.get("suggest_meditation", False) is False


def test_shared_registry_affirmation_does_not_set_flag():
    from app.agent.skills import skill_registry
    result = skill_registry.execute("give_affirmation", {})
    assert result.flags.get("suggest_meditation", False) is False


def test_shared_registry_all_skills_have_nonempty_messages():
    from app.agent.skills import skill_registry
    for name in ("suggest_meditation", "suggest_grounding", "give_affirmation"):
        result = skill_registry.execute(name, {})
        assert len(result.message) > 0, f"{name} returned empty message"

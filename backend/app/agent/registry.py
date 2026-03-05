from typing import Any, Dict, List, Type

from app.agent.base import SkillBase, SkillResult


class SkillRegistry:
    """
    Central registry for all agent skills.

    Usage:
        registry = SkillRegistry()
        registry.register(MeditationSkill)
        registry.register(GroundingSkill)

        tools = registry.get_definitions()       # pass to Anthropic API
        result = registry.execute("suggest_meditation", {})
    """

    def __init__(self) -> None:
        self._skills: Dict[str, SkillBase] = {}

    def register(self, skill_class: Type[SkillBase]) -> None:
        """Instantiate and register a skill by class.
        Re-registering the same skill replaces the previous instance."""
        instance = skill_class()
        self._skills[instance.name] = instance

    def register_instance(self, skill: SkillBase) -> None:
        """Register an already-instantiated skill (e.g. a MarkdownSkill).
        Re-registering the same name replaces the previous instance."""
        self._skills[skill.name] = skill

    def get_definitions(self) -> List[Dict[str, Any]]:
        """Return Anthropic-compatible tool definitions for all registered skills."""
        return [skill.get_definition() for skill in self._skills.values()]

    def execute(self, name: str, args: Dict[str, Any]) -> SkillResult:
        """Dispatch to the named skill and return its SkillResult.
        Returns an error SkillResult (no flags) if the skill is unknown."""
        skill = self._skills.get(name)
        if skill is None:
            return SkillResult(message=f"錯誤：找不到技能 '{name}'。")
        return skill.execute(args)

    def has_skill(self, name: str) -> bool:
        """Return True if the skill name is registered."""
        return name in self._skills

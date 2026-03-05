from pathlib import Path

from app.agent.loader import load_skills_from_dir
from app.agent.registry import SkillRegistry

_SKILLS_DIR = Path(__file__).parent

# Module-level singleton — imported by ChatService.
# To add a new skill: drop a .md file in this directory following the skill
# template format. No Python changes required.
skill_registry = SkillRegistry()
for _skill in load_skills_from_dir(_SKILLS_DIR):
    skill_registry.register_instance(_skill)

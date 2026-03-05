# This module is superseded by the skills-based architecture.
# See: app/agent/skills/__init__.py  →  skill_registry (singleton)
#      app/agent/registry.py         →  SkillRegistry
#      app/agent/base.py             →  SkillBase, SkillResult
#
# Re-exported here so any code that still imports from app.agent.tools
# continues to work without changes.
from app.agent.skills import skill_registry  # noqa: F401

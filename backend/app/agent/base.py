from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class SkillResult:
    """
    Returned by every skill execution.

    `message`  - the text sent back to the LLM as the tool result, and used
                 as the final reply to the user when the skill short-circuits
                 the agentic loop.
    `flags`    - arbitrary key/value metadata propagated to the API response.
                 e.g. {"suggest_meditation": True}
    """
    message: str
    flags: Dict[str, Any] = field(default_factory=dict)


class SkillBase(ABC):
    """Abstract base class every agent skill must implement."""

    #: Exact string the LLM will call, e.g. "suggest_meditation"
    name: str

    #: Human-readable description fed to the Anthropic tools API
    description: str

    def get_definition(self) -> Dict[str, Any]:
        """Return the Anthropic-compatible tool definition dict.
        Works for both class-attribute subclasses and instance-attribute
        MarkdownSkill instances."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {"type": "object", "properties": {}},
        }

    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> SkillResult:
        """Run the skill and return a SkillResult."""
        ...

"""OpenAI application service with versioned prompt loading."""

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from fba_advisor.connectors.openai.interfaces import OpenAIConnector
from fba_advisor.connectors.openai.models import OpenAICompletion


@dataclass(frozen=True, slots=True)
class PromptSpec:
    """A versioned prompt reference stored outside Python source code."""

    name: str
    version: int = 1

    @property
    def filename(self) -> str:
        """Return the prompt filename for this version."""
        return f"{self.name}.v{self.version}.md"


class PromptRepository:
    """Filesystem-backed repository for versioned prompts."""

    def __init__(self, root: Path | str = "prompts") -> None:
        """Initialize the repository with the prompt root directory."""
        self._root = Path(root)

    def get(self, spec: PromptSpec) -> str:
        """Return prompt instructions for the requested prompt version."""
        path = self._root / spec.filename
        if not path.is_file():
            msg = f"Prompt file not found: {path}"
            raise FileNotFoundError(msg)
        return path.read_text(encoding="utf-8").strip()


class OpenAIService:
    """Single entry point for all OpenAI-powered intelligence features."""

    _COMPETITION: Final = PromptSpec("competition_analysis")
    _SUMMARY: Final = PromptSpec("summary")
    _REVIEWS: Final = PromptSpec("review_analysis")
    _BRANDABILITY: Final = PromptSpec("brandability")
    _DIFFERENTIATION: Final = PromptSpec("differentiation")
    _AI_SCORING: Final = PromptSpec("ai_scoring")

    def __init__(self, connector: OpenAIConnector, prompts: PromptRepository | None = None) -> None:
        """Inject the OpenAI connector and prompt repository."""
        self._connector = connector
        self._prompts = prompts or PromptRepository()

    def analyse_concurrence(self, value: str) -> OpenAICompletion:
        """Run the competition analysis prompt."""
        return self._run(self._COMPETITION, value)

    def resume(self, value: str) -> OpenAICompletion:
        """Run the summary prompt."""
        return self._run(self._SUMMARY, value)

    def analyse_avis(self, value: str) -> OpenAICompletion:
        """Run the review analysis prompt."""
        return self._run(self._REVIEWS, value)

    def brandabilite(self, value: str) -> OpenAICompletion:
        """Run the brandability prompt."""
        return self._run(self._BRANDABILITY, value)

    def differenciation(self, value: str) -> OpenAICompletion:
        """Run the differentiation prompt."""
        return self._run(self._DIFFERENTIATION, value)

    def scoring_ia(self, value: str) -> OpenAICompletion:
        """Run the AI scoring prompt."""
        return self._run(self._AI_SCORING, value)

    def _run(self, spec: PromptSpec, value: str) -> OpenAICompletion:
        instructions = self._prompts.get(spec)
        return self._connector.complete(instructions, value.strip())

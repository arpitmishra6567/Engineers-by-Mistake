"""
Deterministic mock model adapter for testing and harness demonstration.
Clearly labeled as a mock to prevent false claims of LLM reasoning.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from repairforge.models.base import BaseModelAdapter, Message, ModelResponse

logger = logging.getLogger(__name__)


class MockModelAdapter(BaseModelAdapter):
    """
    Deterministic mock model adapter.
    Produces canned, predictable responses for demonstration and regression testing.
    """

    def __init__(self, model_name: str = "mock-repair-model", **kwargs: Any) -> None:
        super().__init__(model_name=model_name, **kwargs)
        self.generation_count = 0

    @property
    def is_deterministic(self) -> bool:
        return True

    def generate(self, messages: List[Message], **kwargs: Any) -> ModelResponse:
        """
        Generate a deterministic response based on the message content.
        Flags all responses with is_mock=True.
        """
        self.generation_count += 1
        system_text = " ".join([m.content for m in messages if m.role.value == "system"]).lower()
        user_text = " ".join([m.content for m in messages if m.role.value == "user"]).lower()
        all_text = f"{system_text} {user_text}"

        logger.info(
            "[MOCK INFERENCE] MockModelAdapter generating deterministic response "
            "(Not a real LLM reasoning output)"
        )

        # Check for specific tasks in prompt - prioritize patch generation when requested
        if (
            "patch" in system_text
            or "unified diff" in user_text
            or "code repair" in system_text
            or "code patch" in user_text
        ):
            content = self._mock_patch_response(user_text)
        elif "root cause" in system_text or "diagnose" in user_text or "root cause" in user_text:
            content = self._mock_root_cause_response(user_text)
        else:
            content = (
                "[MOCK RESPONSE] Analysis completed deterministically. "
                "No external reasoning model was invoked."
            )

        return ModelResponse(
            content=content,
            model_name=self.model_name,
            provider="mock",
            is_mock=True,
            prompt_tokens=len(all_text.split()),
            completion_tokens=len(content.split()),
        )

    def _mock_root_cause_response(self, prompt: str) -> str:
        if "average" in prompt or "zerodivisionerror" in prompt or "division by zero" in prompt:
            return (
                "ROOT_CAUSE: ZeroDivisionError occurs when calculating average of an empty list.\n"
                "FILE: average.py\n"
                "FUNCTION: calculate_average\n"
                "EXPLANATION: The calculate_average function executes `sum(numbers) / len(numbers)` "
                "without verifying whether `len(numbers) == 0`. When an empty list is passed, "
                "`len(numbers)` is 0, raising ZeroDivisionError instead of ValueError as expected.\n"
                "UNCERTAINTY: LOW\n"
                "EVIDENCE: ZeroDivisionError: division by zero stack trace on empty input."
            )
        return (
            "ROOT_CAUSE: Generic defect identified.\n"
            "EXPLANATION: Deterministic mock analysis identified condition failure.\n"
            "UNCERTAINTY: MEDIUM\n"
            "EVIDENCE: Test failure exit code 1."
        )

    def _mock_patch_response(self, prompt: str) -> str:
        if "average" in prompt or "division by zero" in prompt or "empty" in prompt:
            return (
                "--- a/average.py\n"
                "+++ b/average.py\n"
                "@@ -10,2 +10,4 @@\n"
                "     \"\"\"\n"
                "+    if not numbers:\n"
                "+        raise ValueError(\"Cannot calculate average of an empty list\")\n"
                "     return sum(numbers) / len(numbers)\n"
            )
        return (
            "--- a/module.py\n"
            "+++ b/module.py\n"
            "@@ -1,2 +1,3 @@\n"
            "+# Mock fix applied\n"
            " pass\n"
        )

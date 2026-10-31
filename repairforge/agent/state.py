"""
State machine and transition validation for RepairForge AI.
Enforces checkpoint-based workflow progression.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class AgentState(str, Enum):
    """Execution states for the repair workflow."""
    # Active checkpoint states
    INITIALIZED = "INITIALIZED"
    REPOSITORY_ANALYZED = "REPOSITORY_ANALYZED"
    ISSUE_UNDERSTOOD = "ISSUE_UNDERSTOOD"
    REPRODUCTION_ATTEMPTED = "REPRODUCTION_ATTEMPTED"
    REPRODUCED = "REPRODUCED"
    ROOT_CAUSE_IDENTIFIED = "ROOT_CAUSE_IDENTIFIED"
    PATCH_GENERATED = "PATCH_GENERATED"
    PATCH_VALIDATED = "PATCH_VALIDATED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    COMPLETED = "COMPLETED"

    # Failure / Terminal states
    NOT_REPRODUCED = "NOT_REPRODUCED"
    ROOT_CAUSE_UNCERTAIN = "ROOT_CAUSE_UNCERTAIN"
    PATCH_GENERATION_FAILED = "PATCH_GENERATION_FAILED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    EXECUTION_BLOCKED = "EXECUTION_BLOCKED"


class StateTransitionRecord(BaseModel):
    """Record of an individual state transition."""
    from_state: AgentState
    to_state: AgentState
    timestamp: float = Field(default_factory=time.time)
    reason: Optional[str] = None


class InvalidStateTransitionError(Exception):
    """Raised when an illegal state transition is attempted."""
    def __init__(self, from_state: AgentState, to_state: AgentState, reason: Optional[str] = None):
        msg = f"Invalid state transition from {from_state.value} to {to_state.value}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason


# Explicit state transition map
# Maps current state -> set of permissible next states
VALID_TRANSITIONS: Dict[AgentState, Set[AgentState]] = {
    AgentState.INITIALIZED: {
        AgentState.REPOSITORY_ANALYZED,
        AgentState.EXECUTION_BLOCKED,
    },
    AgentState.REPOSITORY_ANALYZED: {
        AgentState.ISSUE_UNDERSTOOD,
        AgentState.EXECUTION_BLOCKED,
    },
    AgentState.ISSUE_UNDERSTOOD: {
        AgentState.REPRODUCTION_ATTEMPTED,
        AgentState.EXECUTION_BLOCKED,
    },
    AgentState.REPRODUCTION_ATTEMPTED: {
        AgentState.REPRODUCED,
        AgentState.NOT_REPRODUCED,
        AgentState.EXECUTION_BLOCKED,
    },
    AgentState.REPRODUCED: {
        AgentState.ROOT_CAUSE_IDENTIFIED,
        AgentState.ROOT_CAUSE_UNCERTAIN,
        AgentState.EXECUTION_BLOCKED,
    },
    AgentState.ROOT_CAUSE_IDENTIFIED: {
        AgentState.PATCH_GENERATED,
        AgentState.PATCH_GENERATION_FAILED,
        AgentState.EXECUTION_BLOCKED,
    },
    AgentState.PATCH_GENERATED: {
        AgentState.PATCH_VALIDATED,
        AgentState.VALIDATION_FAILED,
        AgentState.PATCH_GENERATION_FAILED,
        AgentState.EXECUTION_BLOCKED,
    },
    AgentState.PATCH_VALIDATED: {
        AgentState.HUMAN_REVIEW,
        AgentState.EXECUTION_BLOCKED,
    },
    AgentState.VALIDATION_FAILED: {
        # Retry loop allows attempting another patch if retry budget remains
        AgentState.PATCH_GENERATED,
        AgentState.EXECUTION_BLOCKED,
    },
    AgentState.PATCH_GENERATION_FAILED: {
        # Retry loop allows attempting another patch if retry budget remains
        AgentState.PATCH_GENERATED,
        AgentState.EXECUTION_BLOCKED,
    },
    AgentState.HUMAN_REVIEW: {
        AgentState.COMPLETED,
        # Rejection can trigger regeneration or block
        AgentState.PATCH_GENERATED,
        AgentState.EXECUTION_BLOCKED,
    },
    # Terminal states have no valid onward transitions
    AgentState.COMPLETED: set(),
    AgentState.NOT_REPRODUCED: set(),
    AgentState.ROOT_CAUSE_UNCERTAIN: set(),
    AgentState.EXECUTION_BLOCKED: set(),
}


class StateMachine:
    """Manages state transitions and maintains execution history."""

    def __init__(self, initial_state: AgentState = AgentState.INITIALIZED):
        self.current_state = initial_state
        self.history: List[StateTransitionRecord] = []

    def can_transition(self, to_state: AgentState) -> bool:
        """Check if transition to target state is legally permitted."""
        allowed = VALID_TRANSITIONS.get(self.current_state, set())
        return to_state in allowed

    def transition(self, to_state: AgentState, reason: Optional[str] = None) -> StateTransitionRecord:
        """Execute a state transition or raise InvalidStateTransitionError."""
        if not self.can_transition(to_state):
            raise InvalidStateTransitionError(self.current_state, to_state, reason)

        record = StateTransitionRecord(
            from_state=self.current_state,
            to_state=to_state,
            reason=reason,
        )
        self.current_state = to_state
        self.history.append(record)
        return record

"""Unit tests for the state machine and transition validation."""

import pytest
from repairforge.agent.state import (
    AgentState,
    StateMachine,
    InvalidStateTransitionError,
    VALID_TRANSITIONS,
)


def test_valid_state_transitions():
    """Verify standard happy-path state progression."""
    sm = StateMachine(AgentState.INITIALIZED)
    assert sm.current_state == AgentState.INITIALIZED

    rec1 = sm.transition(AgentState.REPOSITORY_ANALYZED, reason="Scanned files")
    assert sm.current_state == AgentState.REPOSITORY_ANALYZED
    assert rec1.from_state == AgentState.INITIALIZED
    assert rec1.to_state == AgentState.REPOSITORY_ANALYZED

    sm.transition(AgentState.ISSUE_UNDERSTOOD)
    sm.transition(AgentState.REPRODUCTION_ATTEMPTED)
    sm.transition(AgentState.REPRODUCED)
    sm.transition(AgentState.ROOT_CAUSE_IDENTIFIED)
    sm.transition(AgentState.PATCH_GENERATED)
    sm.transition(AgentState.PATCH_VALIDATED)
    sm.transition(AgentState.HUMAN_REVIEW)
    sm.transition(AgentState.COMPLETED)

    assert sm.current_state == AgentState.COMPLETED
    assert len(sm.history) == 9


def test_invalid_state_transition_raises():
    """Verify illegal transitions raise InvalidStateTransitionError."""
    sm = StateMachine(AgentState.INITIALIZED)

    # Cannot jump from INITIALIZED directly to COMPLETED or PATCH_GENERATED
    with pytest.raises(InvalidStateTransitionError, match="Invalid state transition from INITIALIZED to COMPLETED"):
        sm.transition(AgentState.COMPLETED)

    with pytest.raises(InvalidStateTransitionError):
        sm.transition(AgentState.PATCH_GENERATED)


def test_validation_failure_allows_retry():
    """Verify that VALIDATION_FAILED allows transition back to PATCH_GENERATED."""
    sm = StateMachine(AgentState.PATCH_GENERATED)
    sm.transition(AgentState.VALIDATION_FAILED, reason="Tests failed")
    assert sm.current_state == AgentState.VALIDATION_FAILED

    # Can transition back to PATCH_GENERATED for a retry
    sm.transition(AgentState.PATCH_GENERATED, reason="Retry attempt 2")
    assert sm.current_state == AgentState.PATCH_GENERATED


def test_terminal_states_have_no_transitions():
    """Verify terminal states like COMPLETED and NOT_REPRODUCED allow no further transitions."""
    sm = StateMachine(AgentState.COMPLETED)
    assert sm.can_transition(AgentState.INITIALIZED) is False
    assert sm.can_transition(AgentState.PATCH_GENERATED) is False

    with pytest.raises(InvalidStateTransitionError):
        sm.transition(AgentState.INITIALIZED)


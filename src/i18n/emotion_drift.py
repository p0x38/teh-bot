from datetime import datetime

from pytz import UTC

from .types import ActionType, UserEmotionState


def update_emotion(state: UserEmotionState, action: ActionType):
    if action == ActionType.SPAM_LEVEL:
        state.annoyance += 0.1 * (1 + state.annoyance * 2)
        state.friendliness -= 0.05
    if action == ActionType.NORMAL_USE:
        state.friendliness += 0.02
    if action == ActionType.POSITIVE_INTERACTION:
        state.friendliness += 0.1
        state.annoyance -= 0.1

    state.friendliness = max(-1, min(1, state.friendliness))
    state.annoyance = max(-1, min(1, state.annoyance))

    return state


def decay_emotion(state: UserEmotionState) -> UserEmotionState:
    now = datetime.now(UTC)
    delta = now - state.last_seen

    seconds = delta.total_seconds()

    decay_factor = 1 - pow(.5, seconds / 1800)

    state.annoyance *= (1 - decay_factor)
    state.friendliness *= (1 - decay_factor * 0.5)

    state.last_seen = now

    return state

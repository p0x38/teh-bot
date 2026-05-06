import math
from datetime import datetime, timedelta

from pytz import UTC

from ..databases.core import Database
from .types import EmotionType, UserEmotionState


def resolve_emotion(state: UserEmotionState) -> EmotionType:
    if state.annoyance > 0.6:
        return EmotionType.MAD
    if state.annoyance > 0.3:
        return EmotionType.ANNOYED
    if state.annoyance < -0.3 or state.friendliness > 0.5:
        return EmotionType.HAPPY
    if state.friendliness < -0.3:
        return EmotionType.SAD

    return EmotionType.NEUTRAL


async def process_emotion(
    db: Database,
    user_id: int,
    burst_window: timedelta = timedelta(seconds=10),
    base_increment: float = 0.05,
):
    state = await db.get_emotion_state(user_id)

    now = datetime.now(UTC)
    delta = now - state.last_seen

    if delta < burst_window:
        factor = math.exp((burst_window - delta).total_seconds() / burst_window.total_seconds())
        state.annoyance += base_increment * factor
    else:
        state.annoyance *= 0.9

    state.annoyance = max(-1.0, min(1.0, state.annoyance))
    state.last_seen = now

    await db.save_emotion_state(user_id, state)

    return state

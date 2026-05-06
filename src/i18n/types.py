import random
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Literal, NotRequired, TypedDict


class PersonalityToneType(StrEnum):
    NORMAL = "normal"
    CASUAL = "casual"
    FORMAL = "formal"
    SILLY = "silly"
    CHAOTIC = "chaotic"


class EmotionType(StrEnum):
    NEUTRAL = "neutral"
    ANGRY = "angry"
    SAD = "sad"
    HAPPY = "happy"
    SCARED = "scared"
    ANNOYED = "annoyed"
    MAD = "mad"


class ActionType(StrEnum):
    SPAM_LEVEL = "spam_level"
    NORMAL_USE = "normal_use"
    POSITIVE_INTERACTION = "positive_interaction"


@dataclass
class CommandContext:
    command_name: str
    interaction_type: Literal["slash", "prefix", "button", "modal"]
    subcommand: str | None = None


@dataclass
class UserEmotionState:
    friendliness: float = 0.0
    annoyance: float = 0.0
    last_seen: datetime = field(default_factory=lambda: datetime.now())


@dataclass
class Personality:
    type: PersonalityToneType
    intensity: Literal["low", "normal", "high"]
    disabled: bool = False
    blend: float = 0.0


@dataclass
class I18nContext:
    user_id: str
    is_guild: bool
    is_dm: bool
    locale: str
    hour: int
    is_new_user: bool
    is_admin: bool
    personality: Personality
    emotion: EmotionType
    streak: int
    guild_id: str | None = None
    level: int | None = None
    command: CommandContext | None = None
    bot_nickname: str | None = None
    mutation: float = 0.0


RuleOutput = Callable[[I18nContext], str]


class Rule(TypedDict, total=False):
    match: Callable[[I18nContext], bool]
    replace: RuleOutput
    priority: NotRequired[int]
    weight: NotRequired[float]


RuleSet = list[Rule]

RulesDict = dict[str, dict[str, RuleSet]]


@dataclass
class MutationContext:
    # entropy: float
    tone: PersonalityToneType
    emotion: EmotionType
    seed: int
    mutation: float
    user_id: str
    intensity: float = 0.0

    # @property
    # def chaos(self):
    #    return self.entropy ** 1.7

    # @property
    # def stability(self):
    #    return 1.0 - self.entropy


MutationFn = Callable[[str, MutationContext, float, random.Random], str]


@dataclass
class MutationRule:
    fn: MutationFn
    priority: float = 1.0
    min_entropy: float = 0.0
    max_entropy: float = 1.0


Transform = Callable[[str], str]

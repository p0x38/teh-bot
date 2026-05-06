from .types import Personality, PersonalityToneType

personality_presets: dict[str, Personality] = {
    "neutral": Personality(type=PersonalityToneType.NORMAL, intensity="normal"),
    "casual": Personality(type=PersonalityToneType.CASUAL, intensity="normal"),
    "assistant": Personality(type=PersonalityToneType.FORMAL, intensity="high"),
    "silly": Personality(type=PersonalityToneType.SILLY, intensity="high"),
    "gremlin": Personality(type=PersonalityToneType.CHAOTIC, intensity="high"),
}

default_personality = personality_presets["casual"]

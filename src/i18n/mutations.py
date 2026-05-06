import random

from .types import MutationContext

# def get_rng(ctx: MutationContext):
#    return random.Random(ctx.seed + int(ctx.entropy * 1000))


def chaotic_punctuation(text: str, ctx: MutationContext):
    if ctx.tone != "chaotic" and ctx.mutation < 0.4:
        return text

    intensity = ctx.mutation

    if random.random() < intensity:
        text += "!" * (1 + int(intensity * 4))

    if random.random() < intensity * 0.7:
        text = text.replace(".", "..." if intensity > 0.6 else "..")

    return text


def formal_compression(text: str, ctx: MutationContext):
    if ctx.tone != "formal":
        return text

    text = text.replace("!!!", ".")
    text = text.replace("lol", "")
    return text


def emotion_filter(text: str, ctx: MutationContext):
    intensity = ctx.mutation

    if ctx.emotion == "mad":
        text = "..." + text

    if ctx.emotion == "happy" and intensity < 0.3:
        text += " :D"

    if ctx.emotion == "annoyed":
        if intensity > 0.5:
            text = text.replace("nice", "yeah sure")
        if intensity > 0.8:
            text = text.replace("what", "what.")

    return text


def rare_glitch(text: str, ctx):
    intensity = ctx.mutation

    chance = 0.01 + (intensity ** 2) * 0.3

    if random.random() > chance:
        return text

    mode = random.choice(["upper", "reverse", "stutter"])

    if mode == "upper":
        return text.upper()

    if mode == "reverse":
        return text[::-1]

    if mode == "stutter":
        return " ".join(word[:1] + "-" + word for word in text.split())

    return text


def spacing_distortion(text: str, ctx: MutationContext):
    return text


def alternating_case(text: str, ctx: MutationContext):
    if ctx.mutation < 0.2:
        return text

    result = []
    flip = random.choice([True, False])

    for ch in text:
        if ch.isalpha():
            if flip:
                result.append(ch.upper())
            else:
                result.append(ch.lower())
            flip = not flip
        else:
            result.append(ch)

    return "".join(result)


def random_case(text: str, ctx):
    intensity = ctx.mutation

    if intensity < 0.1:
        return text

    out = []

    for ch in text:
        if ch.isalpha() and random.random() < intensity:
            ch = ch.upper() if random.random() < 0.5 else ch.lower()
        out.append(ch)

    return "".join(out)


def word_case_distortion(text: str, ctx):
    intensity = ctx.mutation

    def mutate_word(w):
        if random.random() < intensity:
            return w.upper() if random.random() < 0.5 else w.lower()
        return w.capitalize() if random.random() < intensity * 0.5 else w

    return " ".join(mutate_word(w) for w in text.split())


def glitch_caps(text: str, ctx):
    intensity = ctx.mutation

    if intensity < 0.3:
        return text

    words = text.split()
    out = []

    for w in words:
        r = random.random()

        if r < intensity * 0.3:
            out.append(w.upper())
        elif r < intensity * 0.6:
            out.append(w.lower())
        elif r < intensity * 0.9:
            out.append(w.capitalize())
        else:
            # "HelLo" style internal chaos
            out.append("".join(
                c.upper() if i % 2 == 0 else c.lower()
                for i, c in enumerate(w)
            ))

    return " ".join(out)

import uuid


def generate_trace_id() -> uuid.UUID:
    return uuid.uuid4()

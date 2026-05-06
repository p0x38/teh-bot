import secrets


def generate_id(size: int = 8) -> str:
    return secrets.token_hex(size).upper()
